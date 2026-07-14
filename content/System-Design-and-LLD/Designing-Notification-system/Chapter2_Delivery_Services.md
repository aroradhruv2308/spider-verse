---
title: "Chapter 2 — Delivery Services: APNs, FCM, SMS, Email"
---

*Notification System — Study Notes*

# 1. The one idea behind this whole chapter

From Chapter 1: your backend cannot reach a user's device directly. For every channel there is a middleman service that already owns the connection to the user, and you deliver by handing your notification to that middleman.

This chapter names the middleman for each channel and explains how each one works:

- **iPhone push** goes through APNs (Apple's service).
- **Android push** goes through FCM (Google's service).
- **SMS** goes through an SMS service like Twilio or Nexmo.
- **Email** goes through an email service like SendGrid or Mailchimp.

**Provider** — in these diagrams and notes, "provider" simply means your own backend, the system you build. It is the box that starts the flow: it builds the notification and sends it to the middleman. Don't overthink the word; provider = your backend.

# 2. iOS push notification — APNs

The flow: Provider (your backend) → APNs → iPhone.

**APNs (Apple Push Notification Service)** — a service run by Apple whose job is to deliver push notifications to iPhones. Apple owns iOS and every iPhone, so Apple is the only path to the iPhone's screen.

Why it must work this way: every iPhone holds one open connection to Apple's servers at all times. Your backend has no connection to a stranger's iPhone. So the only way to push a notification onto that phone is to give it to Apple, and Apple pushes it down its own already-open connection to the phone.

## What your backend sends to APNs

To send one notification, your backend gives APNs two things:

**Device token** — a unique ID string that identifies one specific phone. It is how Apple knows which of the billion iPhones to deliver to. The phone receives this token from Apple when the app is installed, and the app sends it back to your backend to store. Think of it as the phone's delivery address — not the message, and not a phone number.

**Payload** — the actual content of the notification, written as JSON. It holds things like the title, the body text, and a badge number (the small red count on the app icon).

**JSON (JavaScript Object Notation)** — a plain-text way of writing structured data as key-and-value pairs inside curly braces. It is just a format both sides agree on so the data is readable by machines.

A payload looks like this:

```json
{
  "aps": {
    "alert": {
      "title": "Game Request",
      "body": "Bob wants to play chess",
      "action-loc-key": "PLAY"
    },
    "badge": 5
  }
}
```

So the three components for iOS push are: your Provider (backend), APNs (Apple's delivery service), and the iOS device (the end phone that receives it).

# 3. Android push notification — FCM

The flow: Provider → FCM → Android phone. Same shape as iOS, different middleman — but Android needs extra explanation, because the ownership is not as simple as Apple's.

**FCM (Firebase Cloud Messaging)** — Google's service for delivering push notifications to Android phones. Firebase is Google's brand name for a set of developer tools; FCM is the notification tool inside it.

## Why Android is more complicated than iOS

**Android is open source**. Open source means the code that makes the operating system work is published publicly, and anyone can download it, change it, and build their own phone operating system from it. Google released Android this way on purpose, so phone makers would use it instead of building an operating system from scratch.

**Operating system (OS)** — the core software that runs a device and controls everything — how apps run, how they use the hardware, how they use the battery. Android is an OS; iOS is an OS.

So a fair question is: if Android is open and not owned by Google the way iOS is owned by Apple, why does everyone use Google's FCM? The answer is Google Play Services.

## Google Play Services — the key to the whole thing

**Google Play Services** — a piece of software that Google owns and controls, which runs on nearly every Android phone. It is separate from the open-source Android code and is private to Google. It handles many jobs for apps: pushing notifications (that is FCM), Google account sign-in, location services, maps, ads, and syncing Google data. It is not just for games.

Here is how Google keeps control even though the operating system is open source. When a phone maker like Samsung builds a phone, they can take the free open-source Android — but the raw version is missing key services and users would not accept it. To get the Google Play Store and a working ecosystem, Samsung must also include Google Play Services. Google's rule is: use our Play Store, and you must bundle Google Play Services too. Samsung agrees, so Google Play Services comes preloaded on the phone.

So Google gave away the operating system for free but kept the important services layer private. That is how billions of Android phones end up tied to Google even though the OS itself is open. **FCM lives inside Google Play Services**, which is why it is the practical notification path for almost every Android phone.

## How FCM actually delivers

Because Google Play Services is already running on the phone, it is already holding an open connection to Google's servers. FCM borrows that connection. The delivery goes like this:

1. Your backend hands the notification to FCM.
2. FCM uses the connection that Google Play Services already holds open to Google's servers.
3. Google's servers push the notification down that connection to the phone.
4. The app on the phone receives it and shows it.

The key point: the connection was already there — Google Play Services opened it when the phone started up. FCM does not open a new one per app; it reuses the single existing pipe. This is the exact same reason iPhones go through APNs: one connection per phone, owned by the OS vendor, shared by all apps.

**The edge cases (good to know, not core)**

A phone maker CAN build an Android phone without Google Play Services (using only the open-source code) — but then FCM does not work, the Play Store is missing, and most apps break. In practice these are rare.

China is the real exception: Google services are blocked there, so makers like Xiaomi and Oppo ship their own notification systems instead of FCM. Huawei built "Huawei Mobile Services" as a replacement after being cut off from Google in 2019.

# 4. APNs and FCM side by side

They do the exact same job — deliver a push notification — for different phone types:

- **APNs (iOS)**: Apple owns the OS and the notification service. One company, fully closed.
- **FCM (Android)**: the OS is open source, but Google still controls the services layer (Google Play Services) that contains FCM. So control is effectively Google's anyway.

A notification system has to support both, because users carry both kinds of phone.

# 5. SMS message

The flow: Provider → SMS service → the user's phone as a text.

**SMS (Short Message Service)** — a plain text message sent to a phone number, delivered over the phone networks (the carrier networks, not the internet directly).

Your backend does not connect to the phone networks itself — arranging deals with every carrier is impractical. Instead you use a third-party SMS service.

**Third-party SMS service** — an outside company that already has the connections to the phone networks and sells access to them. You call their service; they deliver the text. Common ones are Twilio and Nexmo. These are commercial, meaning you pay per message sent.

# 6. Email

The flow: Provider → email service → the user's inbox.

A company can run its own email servers, but most do not. They use a commercial email service instead.

**Commercial email service** — an outside company you route your emails through — common ones are SendGrid and Mailchimp. You hand them the email; they deliver it to the inbox.

Two reasons companies pay for this rather than sending email themselves:

- **Better delivery rate** — delivery rate means the share of your emails that actually land in the inbox instead of the spam folder. These services are good at staying out of spam, which is hard to do yourself.
- **Data analytics** — they report back who opened the email, who clicked a link, and so on. Building that tracking yourself is a lot of work.

# 7. The full picture

Putting all four channels together: on one side is a single Provider (your backend). In the middle is a group of third-party services — APNs, FCM, the SMS service, and the email service. On the other side are the four destinations — iPhone, Android phone, a phone receiving SMS, and an email inbox.

**The lesson of the full diagram**

All four delivery services are outside your control — you do not own them. Your backend's job is only to build the notification correctly and hand it to the right third party. That third party owns the connection to the user and does the final step. This one pattern repeats across every channel.

**One misconception to kill**: the device token is not the message and not the phone number. It is only an ID that tells the middleman which device to deliver to. The message content lives in the payload. One is the address, the other is the letter — two separate things.

## Terms in this chapter

**Provider** — your own backend that builds and sends the notification.

**APNs (Apple Push Notification Service)** — Apple's service that delivers push notifications to iPhones.

**FCM (Firebase Cloud Messaging)** — Google's service that delivers push notifications to Android phones; lives inside Google Play Services.

**Device token** — a unique ID for one specific device, telling the middleman where to deliver. Not the message, not a phone number.

**Payload** — the notification's actual content, written in JSON.

**JSON (JavaScript Object Notation)** — a plain-text format for structured data as key-and-value pairs in curly braces.

**Open source** — code published publicly that anyone can download, change, and build on.

**Operating system (OS)** — the core software that runs a device and controls everything on it.

**Google Play Services** — Google's private software preloaded on Android phones that handles notifications, sign-in, maps, ads, and more.

**SMS (Short Message Service)** — a plain text message sent to a phone number over the carrier networks.

**Third-party SMS service** — an outside company (Twilio, Nexmo) that delivers SMS for you, paid per message.

**Commercial email service** — an outside company (SendGrid, Mailchimp) you route emails through, for better delivery rate and analytics.

**Delivery rate** — the share of emails that reach the inbox instead of spam.
