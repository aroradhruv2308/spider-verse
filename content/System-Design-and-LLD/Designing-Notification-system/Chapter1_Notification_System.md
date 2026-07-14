---
title: "Chapter 1 — What a Notification System Is"
---

*Notification System — Study Notes*

# 1. What a notification system is

A notification system is the part of a company's backend whose job is to deliver short messages to users when something happens — a new message, a payment, a friend request, a reminder. The event happens somewhere inside the system, and the notification system is what makes sure the user actually finds out about it.

**Backend** — the server-side software a company runs, the part users don't see. It stores data, runs the business logic, and talks to the outside world. The notification system lives inside this backend.

The important idea to hold onto from the start: the notification system does not decide business things (it doesn't decide that you got a payment). Something else in the backend decides that, and then hands the fact over to the notification system, whose only job is delivery.

# 2. Why it is treated as its own system

You might ask why delivering a message needs a whole system. The reason is that "deliver a message to a user" is harder than it sounds once you look closely:

- A user can be reached in several different ways — a push notification on their phone, an SMS text, an email. Each of these works completely differently underneath.
- The same event might need to go out to millions of users at once, not just one.
- The system that generates the event should not have to know all the messy details of how to reach each user. It just wants to say "notify this user" and move on.

So the notification system exists to hide all this mess behind one clean job: take an event, figure out how to reach the user, and deliver it. Everything else in the backend can then stay simple and just ask the notification system to do the delivery.

# 3. The channels — the ways a user gets reached

**Channel** — one specific way of reaching a user. The four common channels are:

- **Push notification** — the alert that pops up on a phone's screen or lock screen. Different for iPhone (iOS) and Android.
- **SMS** — a plain text message sent to a phone number. SMS stands for Short Message Service.
- **Email** — a message delivered to the user's email inbox.

The same notification system usually supports all of these, because different situations call for different channels. An urgent alert might go as a push notification; a receipt might go as an email. Chapter 2 covers how each of these channels actually delivers a message.

# 4. The one rule that shapes everything: you cannot reach the device directly

This is the single most important idea in the whole topic, and it is worth slowing down on.

Your backend cannot open a direct line to a random user's phone and push a notification onto its screen. The phone is not sitting there waiting for your server, or any server, to call it. If it were, thousands of companies would all be opening connections to every phone, which would drain the battery and flood the network.

**Connection** — a live communication line held open between two machines. It sits in memory on both ends and stays open until one side closes it. Holding one open costs resources, so a phone cannot afford to hold thousands of them.

Because of this, every channel works through a middleman — an outside service that already owns the connection to the user. Your backend hands the notification to that middleman, and the middleman does the last step of delivery. You never touch the device yourself.

**The core pattern to memorise**

Your backend builds the notification, then hands it to a delivery service (a middleman). That service owns the actual connection to the user's device and does the final delivery. This is true for every channel — push, SMS, and email. Chapter 2 names each middleman.

# 5. Push vs. pull — why notifications need "push"

There are two basic ways data can move between a client and a server. Understanding the difference explains why notifications are built the way they are.

**Client** — the user's side (their phone, their app, their browser). **Server** — the company's side that holds the data and does the work.

**Pull (also called polling)** — the client keeps asking the server "anything new for me?" on a timer. The server can only answer questions; it can never speak first. This is how a normal API call works — the client asks, the server replies, done.

**Push** — the server sends data to the client the moment it has something, without being asked. This needs a connection that is already open, because the server has to have a line to speak through.

A notification is the server wanting to tell the client something the client never asked for and can't predict. That is push by definition. A pull-based design would mean the phone constantly asking "any notifications? any notifications?", which is slow and wasteful. So notifications are push-based — which is exactly why the middleman services in Chapter 2 exist: they hold the open connection that makes push possible.

**API call** — API stands for Application Programming Interface. In everyday backend work it means one machine calling another over the network to ask for something and get a reply. This is the normal pull pattern: client asks, server answers, connection closes.

# 6. The shape of the whole system, at a high level

Putting the pieces together, a notification system does roughly this, in order:

- **An event happens** somewhere in the backend (a message arrives, a payment clears).
- **That event is handed to the notification system**, which is told which user to notify.
- **The notification system figures out the channel** — should this go as a push, an SMS, or an email? — and which device or address to target.
- **It builds the notification** in the format the middleman for that channel expects.
- **It hands the notification to the right middleman service**, which does the final delivery to the user's device.

Chapter 2 goes into step five in detail — the actual middleman services for each channel (APNs for iPhone, FCM for Android, SMS services, and email services) and how each one works.

## Terms in this chapter

**Notification system** — the backend part whose job is to deliver short messages to users when events happen.

**Backend** — the server-side software a company runs that users don't see.

**Channel** — one specific way of reaching a user — push, SMS, or email.

**Connection** — a live communication line held open between two machines, sitting in memory on both ends.

**Middleman (delivery service)** — an outside service that owns the connection to the user and does the final delivery on your behalf.

**Client / Server** — the user's side / the company's side.

**Pull (polling)** — the client repeatedly asks the server for anything new; the server can only answer.

**Push** — the server sends data the moment it has it, without being asked; needs an open connection.

**API call** — one machine calling another over the network to ask for something and get a reply.
