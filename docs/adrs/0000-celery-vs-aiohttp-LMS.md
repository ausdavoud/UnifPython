---
date: 2025-03-07
---

# Celery vs. Aiohttp for LMS

## Context and Problem Statement

1. Should we consider scraping courses on LMS in different celery tasks, or one celery task which includes asynchronous http requests?

## Considered Options

* Use a different celery task for each request to LMS.
* Use a single celery task which includes async requests to LMS.

## Decision Outcome

Chosen option: "Use a single celery task which includes async requests to LMS".

## Pros and Cons of the Options

### Use a different celery task for each request to LMS

* Good, because celery has built-in reload strategy.
* Good, because if one request fails, others don't.
* Bad, because each task creates a different session, acquires
memory and adds overload.
* Bad, because this task (scraping LMS) run on short intervals (5 min).

### Use a single celery task which includes async requests to LMS.

* Good, it imposes less overload to server.
* Bad, because it requires making a retry-strategy.

## More Information

I chose the first option because on large scales, e.g. having 100 users, running this task every 5 minutes (or even less) on a new celery worker requires a lot of resources (1400 celery tasks per minute). This decisions is apposed to the next one, where sending notifications to telegram only happens if there is a new message (contrary to this task which must run every x minutes, regardless of actually having new messages on LMS or not).
Plus, each student can have at most 14 courses each semester, and sending 14 async request in a session is not a big deal for aiohttp. I give up on the retry strategy, but might implement one that Grok suggested (decorator-styled).
Last but not least, I want to refresh the asyncio knowledge and explore the pitfalls.