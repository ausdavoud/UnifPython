---
date: 2025-03-07
---

# Celery vs. Aiohttp for Telegram

## Context and Problem Statement

1. Should we consider sending notifications to Telegram in different celery tasks, or one celery task which includes asynchronous http requests?

## Considered Options

* Use a different celery task for each notification.
* Use a single celery task which includes async requests to Telegram API.

## Decision Outcome

Chosen option: "Use a different celery task for each notification".

## Pros and Cons of the Options

### Use a different celery task for each notification

* Good, because celery has built-in reload strategy.
* Good, because if one request fails, others don't.
* Bad, because each task creates a different session, acquires
memory and adds overload.

### Use a single celery task which includes async requests to Telegram API

* Good, it imposes less overload to server.
* Bad, because it requires making a retry-strategy.

## More Information

I chose the first option because reliability on user-end is important and celery has built-in retry strategies that help this. 
This way, if a request fails, I'm sure that others are not cancelled consequently.
Last but not least, I want to explore celery and see what happens when we distribute tasks over many celery workers.

I should set a Celery rate_limit (e.g., “20/m” for 20 tasks per minute) to comply with Telegram’s API limits.

