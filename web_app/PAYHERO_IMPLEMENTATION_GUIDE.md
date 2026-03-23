# General Guide: Payhero M-Pesa Integration (STK Push)

This guide provides a modular blueprint for integrating M-Pesa STK Push payments using the Payhero Kenya gateway. It is designed to be applicable to any project requiring a Lipa na M-Pesa automated prompt.

---

## 1. Prerequisites
- **Credentials**: Payhero API Key and Username.
- **Channel**: A registered Channel ID (STK Push channel).
- **Network**: A publicly accessible HTTPS URL for receiving callbacks.

---

## 2. Backend Logic (Node.js Example)

### A. Initiation (Requesting the Prompt)
To trigger an STK Push, send a POST request to the Payhero API.

**Endpoint**: `POST https://backend.payhero.co.ke/api/v2/payments`

**Core Implementation Logic**:
```javascript
const initiatePayment = async (phone, amount, orderId) => {
  // 1. Format Phone: Payhero expects 07xxxxxxxx or 01xxxxxxxx
  const formattedPhone = phone.replace('+254', '0').replace('254', '0');

  // 2. Prepare Payload
  const payload = {
    amount: Math.round(amount),
    phone_number: formattedPhone,
    channel_id: process.env.PAYHERO_CHANNEL_ID,
    provider: "m-pesa",
    external_reference: `REF_${orderId}_${Date.now()}`, // Unique per request
    callback_url: `${process.env.BASE_URL}/api/payments/callback`,
  };

  // 3. API Call with Basic Auth
  const response = await fetch("https://backend.payhero.co.ke/api/v2/payments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Basic ${Buffer.from(`${username}:${apiKey}`).toString("base64")}`,
    },
    body: JSON.stringify(payload),
  });

  return await response.json(); 
  // Returns: { CheckoutRequestID: "...", Status: "Success", ... }
};
```

---

## 3. Determining Transaction Success

Success must be verified using a **two-layer approach**: the Callback (reliable) and Polling (fallback).

### A. Layer 1: The Callback (Server-to-Server)
This is a **public** endpoint on your server that Payhero hits once the user enters their PIN.

**Payload Structure from Payhero**:
```json
{
  "Status": "Success",
  "ResultCode": 0,
  "ResultDesc": "The service request is processed successfully.",
  "MpesaReceiptNumber": "RKT123ABC",
  "ExternalReference": "REF_12345_67890",
  "Amount": 100
}
```

**Success Criteria**:
- `ResultCode === 0` (Integer) or `"0"` (String).
- `Status` is `"Success"` or `"Completed"`.
- **Validation**: Always check that the `ExternalReference` matches an unpaid transaction in your database before updating.

### B. Layer 2: Status Polling (Client-to-Server)
If the callback is delayed (due to network issues), your frontend should "poll" your backend to check the status. Your backend, in turn, can query Payhero directly.

**Query Endpoint**: `GET https://backend.payhero.co.ke/api/v2/transaction-status?reference=YOUR_EXTERNAL_REFERENCE`

```javascript
const checkStatus = async (reference) => {
  const res = await fetch(`https://backend.payhero.co.ke/api/v2/transaction-status?reference=${reference}`, {
    headers: { "Authorization": `Basic ${auth}` }
  });
  const data = await res.json();
  
  // Successful transaction returns:
  // { status: "Success", provider_reference: "M-PESA_RECEIPT", ... }
  return data.status.toLowerCase() === "success";
};
```

---

## 4. Frontend User Experience (UX)

To ensure a smooth payment flow:
1.  **Loading State**: Disable the "Pay" button immediately after click.
2.  **Waiting Message**: Display: *"A prompt has been sent to [Phone]. Please enter your M-Pesa PIN."*
3.  **Polling Loop**: Use a `setInterval` to call your backend every 5 seconds.
4.  **Timeout**: Stop polling after 60–90 seconds if no status change is detected, and advise the user to check their M-Pesa messages.

---

## 5. Summary of Status Codes
| Code | Meaning | Action |
| :--- | :--- | :--- |
| **0** | **Success** | Deliver product/service. |
| **1** | Insufficient Funds | Ask user to top up and retry. |
| **1032** | Cancelled by User | Allow user to retry. |
| **1037** | Timeout | Poll again or ask user to check their phone. |
| **2001** | Invalid Initiator | Check your Payhero credentials. |

---

## 6. Security Best Practices
- **Public vs. Private**: The `/callback` route must be **public** (no JWT/Auth) so Payhero can send data. Use the `ExternalReference` to verify the sender.
- **Reference Generation**: Include a timestamp or random string in your `ExternalReference` to prevent duplicate errors from M-Pesa.
- **HTTPS**: Payhero requires an SSL-secured callback URL.
