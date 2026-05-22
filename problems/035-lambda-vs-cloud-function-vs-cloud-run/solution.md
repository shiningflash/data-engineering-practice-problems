## Solution 35: Lambda vs Cloud Function vs Cloud Run

### Short version you can say out loud

> All three run a small piece of code on demand and bill only when it runs. The choice usually comes down to three things: where the trigger lives, how long the job runs, and whether I want to ship a container or just code. For the scenario in the question, a file lands in an S3 bucket owned by a partner, so the natural trigger lives in AWS. I would put a Lambda there to consume the S3 event, validate, and then push to GCP. If the work were heavier or longer than 15 minutes, I would use Cloud Run on the GCP side instead.

### The three in one sentence each

* **AWS Lambda.** Run a function in response to an event. Zip or container. Max 15 minutes. Most mature in the AWS event ecosystem.
* **Google Cloud Function.** Same idea on GCP. Gen 2 is built on Cloud Run under the hood. Max 60 minutes. Tight integration with GCP triggers.
* **Google Cloud Run.** Run a container. HTTP, Pub/Sub, scheduler, or event triggers. Can run far longer than functions (effectively unlimited with jobs). Closer to "small service" than "function."

### The dimensions that actually matter

| Dimension                          | Lambda           | Cloud Function   | Cloud Run             |
| ---------------------------------- | ---------------- | ---------------- | --------------------- |
| Cloud                              | AWS              | GCP              | GCP                   |
| Code shape                         | Zip or container | Source or container | Container          |
| Max runtime                        | 15 minutes       | 9 min (gen1) / 60 min (gen2) | ~60 min HTTP, unlimited as Job |
| Cold start                         | ~100ms-1s        | ~1-3s            | ~1-3s, can be 0 with min instances |
| Concurrency per instance           | 1                | 1                | Configurable, up to ~1000 |
| Memory cap                         | 10 GB            | 16 GB (gen2)     | 32 GB                 |
| Cost                               | Per invocation + GB-sec | Per invocation + GB-sec | Per second of CPU/memory while running |
| Native triggers                    | All AWS services | All GCP services | HTTP + Pub/Sub + Scheduler + Eventarc |
| When you want a container          | Yes (since 2020) | Yes (gen2)       | Yes (always)          |

### How I would pick for the scenario

The file lands in an AWS bucket. The S3 event is the trigger. Three reasonable patterns:

**Pattern A: Lambda in AWS, push to GCP from there.**

```
S3 (partner)  ──ObjectCreated──▶  Lambda (Python)
                                     │
                                     ▼
                          validate, transform
                                     │
                                     ▼
                   BigQuery load API (cross-cloud HTTPS)
```

* Trigger lives where the data lives. No polling, no cross-cloud event copy.
* Small Python function. Zip or image.
* The cross-cloud call is one HTTPS write to BigQuery's load API. ~1 second.
* Total cost: pennies per day at 200 invocations.

This is what I would actually ship for this scenario.

**Pattern B: copy file to GCS first, then Cloud Function.**

```
S3 (partner)  ──ObjectCreated──▶  Lambda copies to GCS
                                     │
                                     ▼
                                  GCS ObjectFinalized
                                     │
                                     ▼
                          Cloud Function (Python)
                                     │
                                     ▼
                          validate, transform, load BQ
```

Two hops, more moving parts. The reason to do this is if the team has strict "all data must enter GCP first for audit" rules, or if the validation is complex and the team's library is GCP-only.

**Pattern C: Cloud Run with a scheduled poll.**

If the partner cannot fire an event when they drop the file, polling is the fallback. Cloud Scheduler hits a Cloud Run endpoint every 5 minutes, the service lists the S3 bucket, picks up new files, processes them.

I would only do this if S3 event delivery is impossible. Polling wastes invocations and adds latency.

### When I would actually pick each one

**Pick Lambda when:**

* The trigger source is in AWS (S3, DynamoDB, EventBridge, SQS, Kinesis).
* The job is short (< 15 minutes) and stateless.
* You already have AWS IAM and observability set up.

**Pick Cloud Function when:**

* The trigger source is in GCP (GCS, Pub/Sub, Firestore, Eventarc).
* The job is short to moderate (< 60 minutes on gen 2).
* You want the cheapest, simplest deploy.

**Pick Cloud Run when:**

* The job needs to run longer than function limits.
* You need higher concurrency per instance (a web API that handles 100 concurrent users on one container).
* You want a full container, with system dependencies, drivers, larger libraries.
* You need a small HTTP API, not just a one-shot handler.
* You want to keep some instances warm (`min-instances`) to eliminate cold starts.

### Three things people get wrong

**1. Picking Cloud Run when a function is fine.**

Cloud Run takes more operational effort: build an image, manage the Dockerfile, deal with image registry. For a 30-line Python script, a function is faster to ship and equally cheap.

**2. Picking Lambda when the trigger lives in GCP.**

You can do it (EventBridge can subscribe to Pub/Sub), but you are routing data around for no reason. Use the native event source.

**3. Forgetting the 15-minute Lambda limit.**

A "small job" that scans a big bucket can drift past 15 minutes once a file is unusually large. Either bound the work (process up to N files per invocation), or use Cloud Run or Step Functions for the workflow.

### Cold start, in practice

Cold starts matter when the trigger is user-facing. For a file-drop pipeline, a 1-2 second cold start is fine. For an API behind a mobile app, cold starts hurt.

Mitigations:

* **Provisioned concurrency** on Lambda or **min-instances** on Cloud Run / Cloud Function gen2 keeps instances warm. Costs more.
* **Smaller runtime** (avoid large dependencies, use slim base images, lazy-import heavy modules).
* **Smaller package** (avoid bundling unused libraries).

For 200 invocations a day, none of this matters. For 200 per second, it does.

### Cost shape

* **Lambda and Cloud Function** charge per invocation plus per GB-second.
* **Cloud Run** charges per second of CPU and memory while the request is in flight (per-second billing, idle time not charged with concurrency).

For a small 1-second job at 200 invocations a day:

* Lambda: well under a dollar a month.
* Cloud Function: same.
* Cloud Run: same.

The cost choice does not matter until you are running tens of millions of invocations.

### Observability is the deciding factor sometimes

For a Python script you wrote, observability is what saves your week. Each has good logs (CloudWatch, Cloud Logging) and metrics. What I would ask the team:

* Where do we already send logs?
* Where do we have on-call dashboards?
* Where do alerts route?

Putting the function in a cloud where you already have observability set up beats picking the "best" tool but having to wire it from scratch.

### Common mistakes interviewers want you to name

1. **Default to whatever I used last time** without thinking about trigger source.
2. **Picking the wrong runtime cap.** Lambda for a 22-minute job will be a nightmare.
3. **Ignoring cold starts on user-facing paths.**
4. **Over-engineering with Cloud Run** when a function would work fine.
5. **Forgetting cross-cloud egress costs.** Pulling a file out of S3 to process in GCP costs egress.

### Bonus follow-up the interviewer might throw

> *"What if you needed to add a second step that takes the BigQuery load result and emails a report?"*

I would not make the function bigger. I would publish a message ("BQ load completed for file X") to Pub/Sub or EventBridge, and a second function subscribes and sends the email. Two small, single-purpose functions are easier to debug and rerun than one that does both. This is the cloud version of "do one thing well."
