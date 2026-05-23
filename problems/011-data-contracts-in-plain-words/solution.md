## Solution 11: Data Contracts in Plain Words

### Short version you can say out loud

> A data contract is an explicit agreement between the team that produces data and the teams that consume it. It says what fields will be there, what types they will be, what they mean, how fresh they will be, and who owns them. Same idea as an API contract between two services, just applied to data. People are talking about it now because data has become a product, and treating it as a side effect of the app keeps breaking downstream systems.

### Why now

For most of the last 20 years, data was a by-product of the application. Engineers built features and the data team scraped whatever ended up in the database. When the app team changed a column, the data team found out when the dashboard broke the next morning. That worked when there were two analysts and one report. It does not work now, because data feeds machine learning models, billing, regulators, and live customer features. The cost of a breaking change is much higher.

Data contracts are the industry trying to apply software engineering discipline (interfaces, versioning, tests, ownership) to data the same way we did to microservice APIs ten years ago.

### What a contract actually contains

```
                 ┌────────────────────────────────────────┐
                 │              DATA CONTRACT             │
                 │                                        │
                 │   Schema    fields, types, nullability │
                 │   Semantics what each field means      │
                 │   Quality   rules and SLAs             │
                 │   Freshness how often, how late        │
                 │   Owner     team and on-call           │
                 │   Version   semver, deprecation policy │
                 └─────────────┬──────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
        Producer team                    Consumer teams
        (app backend)                    (analytics, ML, finance)
```

A typical YAML contract might look like:

```yaml
name: orders
version: 1.3.0
owner: checkout-team
sla:
  freshness: 5 minutes from event time
  availability: 99.9%
schema:
  - name: order_id
    type: string
    required: true
    description: A unique id for the order. Stable across retries.
  - name: customer_id
    type: int64
    required: true
  - name: amount_cents
    type: int64
    required: true
    description: Charged amount in the smallest unit of the currency.
  - name: currency
    type: string
    required: true
    constraints:
      enum: [SGD, MYR, IDR, USD]
  - name: created_at
    type: timestamp
    required: true
quality:
  - rule: amount_cents > 0
  - rule: order_id is unique
  - rule: no more than 0.01% of rows missing currency
breaking_changes_policy: 6 months deprecation window
```

Same shape as a Protobuf schema, an OpenAPI spec, or an Avro schema, plus extra metadata about ownership and SLA.

### What a contract is NOT

* Not just a document on Confluence. A document does not catch a renamed column at 3 AM.
* Not the same as a schema. A schema only describes shape. A contract also covers meaning, ownership and freshness.
* Not a one-way wish list from the consumer. Both sides have to agree, because the producer takes on the cost of stability.

### Where it gets enforced

The whole point is that the contract is machine readable and checked automatically. Three common enforcement points:

```
┌─────────┐   1   ┌──────────┐   2   ┌──────────┐   3   ┌──────────┐
│Producer │──────▶│  Kafka / │──────▶│  Warehouse│─────▶│ Consumer │
│   code  │       │  S3      │       │           │       │   code   │
└─────────┘       └──────────┘       └──────────┘       └──────────┘
    │                  │                   │
    ▼                  ▼                   ▼
1. CI check in        2. Schema             3. dbt tests against
   producer repo         registry              the contract on
   (a renamed            (Avro / Protobuf,     every model run.
   column fails          rejects messages
   the build)            that don't match
                         the registered
                         schema)
```

* Producer side. A CI test fails the build if a code change would break the contract. This is the most valuable spot, because it catches the issue before it leaves the producer team.
* Ingest side. A schema registry (Confluent, Apicurio, Glue Schema Registry) rejects events that don't match the registered schema. Catches drift between code and reality.
* Consumer side. dbt tests or Great Expectations checks validate the data on arrival. Last line of defence.

### How a real change happens with contracts

The producer team wants to rename `user_id` to `userId`. With a contract in place:

1. They open a pull request that changes the contract: `user_id` is now deprecated in version 1.4, `userId` is added.
2. CI runs the consumer test list against the new contract. It tells them which downstream models reference `user_id` (8 of them).
3. The contract says the deprecation window is 6 months. They cannot remove `user_id` for 6 months. They keep emitting both fields during that window.
4. Consumers migrate at their own pace. After 6 months, the field is removed.

The dashboard never breaks at 3 AM, because the system enforced the agreement.

### Common mistakes

1. **"We have a contract" but it lives in a Google Doc.** Not enforced is not a contract.
2. **The contract is owned by the data team, not the producer team.** Producers will not feel responsible, so it drifts.
3. **No deprecation window.** Producers will still break consumers because they can change the schema instantly.
4. **Treating semantic changes as non breaking.** Renaming the *meaning* of `amount` from "net" to "gross" is a breaking change even if the type and name stay the same.

### Bonus follow-up the interviewer might throw

> *"What is the difference between a data contract and a schema registry?"*

A schema registry enforces shape. The data contract is the bigger agreement that *contains* a schema and adds meaning, ownership, freshness and quality rules. In practice you usually have both: the contract lives in source control, and at runtime, the registry enforces the schema piece of it.
