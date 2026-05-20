## Solution 65: 4000 DAG Airflow at 90 Percent CPU

### Short version you can say out loud

> Before scaling out, I check what the scheduler is actually busy with. In most overloaded Airflows, the cost is DAG parsing, not task scheduling. So the first wins are tuning the parse interval, simplifying or removing expensive DAGs, and using dynamic DAGs more carefully. If after that the scheduler is still hot, then yes, scale the scheduler or split into multiple environments. But scaling first hides a structural problem that will grow back.

### What the scheduler is actually doing

The Airflow scheduler does two main loops:

1. **Parse every DAG file on disk** to understand the dependencies and schedules.
2. **Look at every DAG's run state** and decide which tasks should start now.

For most overloaded Airflows, parsing dominates. The scheduler re-parses each DAG file every few seconds (default 30 seconds) to pick up changes. With 4,000 DAG files, that is a lot of Python imports and constructor calls per minute.

Two practical signals:

* `dag_processor_manager.log` shows how long each file takes to parse.
* `scheduler.heartbeat` lag tells you if the scheduler is keeping up.

If parse time per file is high (multi-second) or total parse cycle is longer than a few minutes, parsing is the problem.

### The first wins (no scaling)

**1. Increase `min_file_process_interval`.**

The default is 30 seconds. If you don't need DAG changes picked up that fast, raise it to 120 seconds or more.

```ini
[scheduler]
min_file_process_interval = 120
```

This single setting can drop scheduler CPU by 50% on large Airflows.

**2. Reduce expensive imports at the top of DAG files.**

Many teams put heavy code at module level:

```python
# bad: runs every parse
import pandas as pd
from some_heavy_library import expensive_thing

big_config = expensive_thing()
```

This executes on every parse cycle. Move the heavy work inside operators or PythonCallables. The parser only needs to know the DAG's shape, not its data.

```python
# better: parser sees a fast import
from airflow import DAG
from airflow.operators.python import PythonOperator

def my_task():
    import pandas as pd
    from some_heavy_library import expensive_thing
    return expensive_thing()
```

A surprising fraction of overloaded Airflows are fixed by this one habit.

**3. Audit dynamic DAGs.**

A team builds a "dynamic DAG factory" that generates 500 DAGs from a config. Each parse iterates the config, generates Python, parses 500 sub-objects. Expensive.

Fixes:

* Cache the config so it loads once per process, not once per DAG.
* Reduce the number of dynamically generated DAGs (use task groups within fewer DAGs).
* Use Airflow's dynamic task mapping for "do the same thing 500 times" patterns, instead of 500 separate DAGs.

**4. Remove dead DAGs.**

Often 10-30% of DAGs are abandoned: nobody uses them, they fail silently, nobody notices. Audit by:

* Which DAGs have not run successfully in 60 days?
* Which DAGs nobody owns?
* Which DAGs produce tables nobody queries?

For each abandoned DAG, find an owner or delete it. Deleting 1,000 DAGs cuts parse load proportionally.

**5. Pause infrequent DAGs that don't need to be parsed all the time.**

A DAG that runs once a month doesn't need to be parsed every 30 seconds. There is no built-in way to vary parse frequency per DAG, but you can:

* Move it to a separate Airflow if you have one.
* Use Airflow's `is_paused_upon_creation` and a scheduled "unpause then run then pause" pattern. More complex.

**6. Use the database scheduler tuning.**

```ini
[scheduler]
parsing_processes = 4               # parse files in parallel
max_threads = 4                     # tasks per scheduler process
```

Tune to the machine. More parsing processes if you have CPU; fewer if you don't.

### When scaling out is the right call

After the above:

* If parse cycle is still slow, run multiple scheduler processes (Airflow 2.0+ supports HA scheduler).
* If task throughput is the bottleneck (you have many tasks queued but workers idle), you might be under-resourced on workers. Scale workers.
* If the DAG count keeps growing past a point (5,000+), consider splitting into multiple Airflow environments, by team or by domain.

Multi-scheduler is the cheapest of these. Two schedulers on the same metadata DB roughly halve the load.

### The structural issue

Airflow with 4,000 DAGs and growing has outgrown its sweet spot. Some honest questions:

* Are 1,000 of those DAGs really one-line tasks that should be tasks within other DAGs?
* Should some workflows move to a lighter scheduler (Cloud Workflows, simple cron) and free Airflow for the complex DAGs?
* Does this team need a self-service "I want to schedule this" tool that doesn't dump every job into Airflow?

This is a longer conversation but worth raising. Otherwise the scale-up cycle continues every six months.

### A migration option: Dagster

If the team is doing a rebuild anyway, Dagster's asset-centric model often handles "many small things" better. You describe the data you want to exist, and Dagster figures out the dependencies. It scales differently than Airflow's DAG-list approach. Not a quick switch, but worth considering when planning the next phase.

### What I would actually do this week

1. Audit parse times per DAG. Identify the top 20 slowest.
2. Fix module-level imports in those 20. Quick wins.
3. Bump `min_file_process_interval` to 120 seconds.
4. Identify and delete abandoned DAGs.
5. Add a "DAG count" tracking metric so the team sees growth pressure.

If those don't drop scheduler CPU below 60%, then I would propose scaling (multi-scheduler).

### Common mistakes interviewers want you to name

1. **Scale-up first.** Hides the parsing problem.
2. **No ownership audit.** Abandoned DAGs accumulate.
3. **Module-level heavy imports.** Single biggest perf trap.
4. **Aggressive dynamic DAG factories.** Often the entire problem.
5. **Default `min_file_process_interval`.** Fine for 100 DAGs, painful for 4000.

### Bonus follow-up the interviewer might throw

> *"What if your team owns 2,000 of those 4,000 DAGs and the other 2,000 are from another team you can't change?"*

Split Airflows. Two environments. Yours is now 2,000 DAGs and you control the practices. Theirs is their problem. Shared metadata DB is a no, separate clusters with their own DBs is a yes. This also gives you isolation in the failure case: if their team breaks their scheduler, yours keeps running.

This is a non-trivial migration, weeks of work. But it solves the structural issue, not just the symptom.
