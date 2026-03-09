# IndustriSense AI - Website & PayHero Integration Guide

## 🎨 Professional Website Updates

The website has been completely redesigned with a modern, professional appearance:

### Design Improvements

**1. Bootstrap 5 Integration**
- Responsive Grid System
- Professional Components (Cards, Badges, Alerts)
- Mobile-First Design
- Built-in Accessibility

**2. Modern Color Scheme**
- Primary Blue (#0d6efd)
- Professional Dark Gray (#212529)
- Success Green (#198754)
- Warning Yellow (#ffc107)
- Danger Red (#dc3545)

**3. Enhanced Navigation**
- Sticky Navbar with Hamburger Menu
- Icon-based Navigation
- Active Page Indicators
- Responsive Collapse

**4. Professional Footer**
- Multiple Columns (About, Links, Connect)
- Social Media Icons
- Copyright Information
- Contact Links

**5. Improved Components**
- Stat Cards with Hover Effects
- Professional Card Designs
- Gradient Buttons
- Shadow Effects & Animations
- Responsive Typography

---

## 💳 PayHero Payment Integration

### Overview

Full payment integration using PayHero for secure, reliable payment processing. Supports:
- M-Pesa (Primary)
- Credit/Debit Cards
- Bank Transfers

### Features Implemented

✅ **Pricing Plans Page** (`/plans`)
- 3 Pricing Tiers (Starter, Professional, Enterprise)
- Feature Comparison
- FAQ Section
- Call-to-Action Buttons

✅ **Checkout Page** (`/checkout/<plan_name>`)
- Order Summary
- Comprehensive Checkout Form
- Form Validation
- Payment Processing UI

✅ **Payment Processing** (`/payment/process`)
- PayHero API Integration
- Payment Initiation
- Error Handling
- Security Implementation

✅ **Payment Success Page** (`/payment/success`)
- Order Confirmation
- Next Steps Guide
- Download Receipts
- Support Links

✅ **Payment Failure Page** (`/payment/failure`)
- Error Information
- Troubleshooting Guide
- Retry Options
- Support Contact

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd web_app
pip install -r requirements.txt
```

### 2. Configure PayHero Credentials

Create a `.env` file in the `web_app` directory:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PAYHERO_API_KEY=your_payhero_api_key
PAYHERO_API_SECRET=your_payhero_api_secret
PAYHERO_SANDBOX=true
PAYMENT_SUCCESS_URL=http://localhost:5000/payment/success
PAYMENT_FAIL_URL=http://localhost:5000/payment/failure
```

### 3. Get PayHero API Credentials

1. Visit [PayHero](https://payhero.io)
2. Create an Account
3. Go to Settings → API Keys
4. Copy your API Key and Secret
5. Set Sandbox Mode to True for testing

### 4. Update Production URLs

When deploying to production, update `.env`:

```env
PAYHERO_SANDBOX=false
PAYMENT_SUCCESS_URL=https://yourdomain.com/payment/success
PAYMENT_FAIL_URL=https://yourdomain.com/payment/failure
```

### 5. Run the Application

```bash
python app.py
```

Or using the run script:

```bash
./run.sh  # Linux/Mac
./run.bat  # Windows
```

---

## 📋 Routes Available

### Payment Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/plans` | GET | View pricing plans |
| `/checkout/<plan>` | GET | Checkout page for a plan |
| `/payment/process` | POST | Process payment with PayHero |
| `/payment/success` | GET | Payment success callback |
| `/payment/failure` | GET | Payment failure callback |
| `/payment/verify` | POST | Verify payment status |

### Existing Routes (Preserved)

| Route | Purpose |
|-------|---------|
| `/` | Dashboard |
| `/analytics` | Analytics Page |
| `/models` | ML Models Information |
| `/predict` | Prediction Interface |
| `/settings` | Settings Page |
| `/about` | About Page |

---

## 🛠️ Technical Details

### Payment Flow

```
User → Plans Page
  ↓
  → Select Plan
  ↓
  → Checkout Page
  ↓
  → Fill Form
  ↓
  → Process Payment (PayHero API)
  ↓
  → PayHero Payment Gateway
  ↓
  → Success/Failure Callback
  ↓
  → Success/Failure Page
```

### PayHero API Integration Points

**Sending Payment Request:**
```python
POST /api/v2/payments
{
    "amount": 2900,
    "currency": "KES",
    "email": "customer@example.com",
    "phone_number": "+254712345678",
    "description": "IndustriSense AI Professional Plan"
}
```

**Verifying Payment:**
```python
GET /api/v2/payments/{payment_id}
```

### Security Features

✅ API Key in Environment Variables (not in code)
✅ HTTPS/TLS Encryption
✅ Form Validation on Frontend & Backend
✅ PayHero's Secure Payment Gateway
✅ CORS Configuration
✅ Session Management
✅ Error Handling & Logging

---

## 📱 Responsive Design

The website is fully responsive:
- **Desktop** (1200px+): Full multi-column layout
- **Tablet** (768px-1199px): Optimized 2-column layout
- **Mobile** (< 768px): Single column, touch-friendly

---

## 🎯 Planning Page Features

### Pricing Tiers

**Starter - $29/month**
- 5 Machines
- Basic Analytics
- Email Support
- Weekly Reports
- Dashboard Access

**Professional - $99/month** ⭐ Most Popular
- 50 Machines
- Advanced Analytics
- Priority Support
- Daily Reports
- API Access
- Custom Alerts
- Data Export

**Enterprise - $299/month**
- Unlimited Machines
- Real-time Predictions
- 24/7 Phone Support
- Hourly Reports
- Advanced API
- Custom Integration
- Dedicated Account Manager

---

## 🔒 Payment Security

1. **No Card Storage**: PayHero handles all card data
2. **SSL/TLS Encryption**: All data transmitted securely
3. **PCI Compliance**: Full PCI DSS compliance
4. **API Key Security**: Stored in environment variables
5. **Session Security**: Secure session handling
6. **Input Validation**: Frontend and backend validation

---

## 🧪 Testing the Payment Integration

### Sandbox Mode

1. Keep `PAYHERO_SANDBOX=true` in `.env`
2. Use test M-Pesa number: `254712345678`
3. All transactions won't be charged
4. Full error handling testing available

### Testing Scenarios

**Successful Payment:**
- Fill form with valid data
- Use sandbox test number
- Confirm payment in M-Pesa prompt
- Should redirect to success page

**Failed Payment:**
- Use incorrect phone number
- Decline payment when prompted
- Insufficient balance
- Should redirect to failure page with error details

---

## 📊 Pricing Page Analytics

Track conversions by monitoring:
- `/plans` page visits
- `/checkout/<plan>` page visits
- `/payment/process` POST requests
- `/payment/success` redirects
- `/payment/failure` redirects

## 🐛 Troubleshooting

### Common Issues

**Issue**: PayHero API key not working
- **Solution**: Check `.env` file has correct keys
- Verify keys in PayHero dashboard
- Ensure sandbox mode matches your account

**Issue**: Phone number validation fails
- **Solution**: Ensure format is `254xxxxxxxxx` (without +)
- Phone must be 9 digits after country code

**Issue**: Payment never completes
- **Solution**: Check internet connection
- Try sandbox testing first
- Contact PayHero support

**Issue**: Redirect loops
- **Solution**: Update success/failure URLs in config
- Ensure routes exist in app.py
- Clear browser cache

---

## 📞 Support

### For Payment Issues
- **PayHero Support**: [support@payhero.io](mailto:support@payhero.io)
- **PayHero Docs**: [https://payhero.io/docs](https://payhero.io/docs)

### For IndustriSense Issues
- **Email**: support@industrisense.ai
- **GitHub**: [Trailblazer-dev/IndustriSense-AI](https://github.com/Trailblazer-dev/IndustriSense-AI)

---

## 🔄 Next Steps

1. ✅ Install dependencies
2. ✅ Configure PayHero API keys
3. ✅ Test in sandbox mode
4. ✅ Deploy to production
5. ✅ Switch to live mode
6. ✅ Monitor payment flows
7. ✅ Gather customer feedback

---

## 📝 Environment Variables Reference

```env
# Flask Configuration
FLASK_ENV=development|production
SECRET_KEY=your-long-secret-key

# PayHero Configuration
PAYHERO_API_KEY=pk_live_xxxxx or pk_test_xxxxx
PAYHERO_API_SECRET=sk_live_xxxxx or sk_test_xxxxx
PAYHERO_SANDBOX=true|false

# Payment URLs
PAYMENT_SUCCESS_URL=https://yourdomain.com/payment/success
PAYMENT_FAIL_URL=https://yourdomain.com/payment/failure
```

---

## ✨ Features Summary

✅ Modern, professional website design
✅ Responsive Bootstrap 5 integration
✅ Complete PayHero payment integration
✅ 3 pricing tiers with features
✅ Detailed checkout process
✅ Payment success/failure handling
✅ API verification endpoints
✅ Comprehensive error handling
✅ Security best practices
✅ Mobile-friendly design
✅ Social media integration
✅ Professional footer
✅ FAQ sections
✅ Clear call-to-action buttons

---

**Status**: ✅ Ready for Production
**Last Updated**: February 22, 2026
