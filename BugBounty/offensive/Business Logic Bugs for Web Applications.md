# Business Logic Bugs for Web Applications

A comprehensive guide to finding and exploiting business logic vulnerabilities.

---

## 1. Negative Price Manipulation

**How it works:**  
Application accepts negative values for prices or quantities without proper server-side validation.

**Steps to Find**
1. Identify price or quantity parameters in checkout flow.
2. Use a proxy tool (Burp Suite) to intercept requests.
3. Modify the price parameter to a negative value (e.g., `-999`).
4. Modify quantity to negative integers.
5. Submit the modified request.
6. Check if the transaction processes with a negative amount.

**Impact**
- Financial loss
- Users receiving products plus money
- Inventory manipulation

---

## 2. Discount / Coupon Stacking Abuse

**How it works:**  
Application fails to verify if a discount was already applied or if the order changed after applying a discount.

**Steps to Find**
1. Add items to cart until discount threshold is met.
2. Apply discount or coupon code.
3. Remove items from cart after discount applied.
4. Complete purchase with discount on reduced order.
5. Try applying multiple expired coupons.
6. Test concurrent coupon redemption requests.

**Impact**
- Revenue loss
- Discount abuse
- Financial fraud

---

## 3. Investment Limit Override

**How it works:**  
Investment limits enforced only in the UI, not on the server.

**Steps to Find**
1. Find investment or transaction limits in documentation.
2. Try exceeding the limit via UI and observe the error.
3. Intercept the transaction request using a proxy.
4. Locate amount or limit parameters in the request.
5. Modify values to exceed documented limits.
6. Check if the transaction processes successfully.

**Impact**
- Risk management failure
- Regulatory exposure
- Financial losses

---

## 4. Workflow Step Bypass

**How it works:**  
Multi-step processes fail to verify completion of previous steps.

**Steps to Find**
1. Identify multi-step workflows (checkout, registration, 2FA).
2. Complete the first step and capture the request.
3. Jump directly to the final step URL.
4. Skip payment or verification steps.
5. Access confirmation pages directly.
6. Check if workflow completes without authentication.

**Impact**
- Authentication bypass
- Payment bypass
- Privilege escalation

---

## 5. Race Condition Exploitation

**How it works:**  
Simultaneous requests bypass balance or inventory checks due to poor locking mechanisms.

**Steps to Find**
1. Identify critical operations such as withdrawals or redemptions.
2. Send a legitimate request first.
3. Use Turbo Intruder or a custom script.
4. Send multiple concurrent identical requests.
5. Check if all requests succeed despite constraints.
6. Verify balance or inventory changes.

**Impact**
- Double spending
- Overdrafts
- Inventory overselling
- Unlimited redemptions

---

## 6. Client-Side Price Manipulation

**How it works:**  
Prices stored in hidden fields or client-side parameters without server validation.

**Steps to Find**
1. Inspect HTML source for hidden price fields.
2. Use browser developer tools to modify values.
3. Intercept POST request using a proxy.
4. Locate the price parameter (e.g., `price=100`).
5. Change to an arbitrary value (`price=1`).
6. Complete transaction with modified price.

**Impact**
- Revenue loss
- Fraud
- Inventory given away

---

## 7. Parameter Tampering

**How it works:**  
User roles, permissions, or sensitive data passed in client-controllable parameters.

**Steps to Find**
1. Capture requests containing parameters like `role=user`.
2. Identify privilege indicators.
3. Modify them to elevated values (`role=admin`).
4. Change user IDs to access other accounts.
5. Alter boolean flags (`isAdmin=true`).
6. Attempt access to restricted resources.

**Impact**
- Privilege escalation
- Unauthorized access
- Authorization bypass

---

## 8. Refund / Return Abuse

**How it works:**  
System does not validate if an order was already refunded.

**Steps to Find**
1. Complete a legitimate purchase.
2. Request a refund through normal flow.
3. Capture and replay the refund request.
4. Check if duplicate refunds are blocked.
5. Attempt refunding an already refunded order.
6. Test cancellation of shipped orders.

**Impact**
- Financial loss
- Inventory discrepancies
- Fraud

---

## 9. Two-Factor Authentication Bypass

**How it works:**  
2FA verification is not enforced on subsequent requests.

**Steps to Find**
1. Start login with valid credentials.
2. Reach the 2FA verification page.
3. Note the destination URL after 2FA.
4. Directly access the destination without completing 2FA.
5. Check if session grants access.
6. Verify whether 2FA token validation occurs.

**Impact**
- Authentication bypass
- Account takeover

---

## 10. Inventory Reservation Without Payment

**How it works:**  
Items remain reserved in the cart without purchase.

**Steps to Find**
1. Add high-demand items to the cart.
2. Abandon the cart without purchasing.
3. Check if inventory remains reserved.
4. Add maximum quantities and abandon.
5. Test timeout mechanisms.
6. Verify if items remain unavailable to others.

**Impact**
- Denial of service
- Inventory manipulation
- Revenue loss

---

## 11. Integer Overflow / Underflow

**How it works:**  
Extreme values cause calculation errors.

**Steps to Find**
1. Identify numeric input fields.
2. Test with maximum integer values.
3. Try boundary values like `2147483647`.
4. Use values that overflow to negative.
5. Test decimal values where integers expected.
6. Check results for anomalies.

**Impact**
- Free products
- Incorrect charges
- System crashes

---

## 12. Order Modification After Approval

**How it works:**  
Orders can be modified after approval but before fulfillment.

**Steps to Find**
1. Place and approve an order.
2. Capture order confirmation request.
3. Identify modification endpoints.
4. Attempt modifying approved order details.
5. Change quantities or items.
6. Check if modifications are processed.

**Impact**
- Fraud
- Inventory issues
- Fulfillment errors

---

## 13. Session Fixation in State Transitions

**How it works:**  
Session state not validated properly during workflow transitions.

**Steps to Find**
1. Start workflow with one role.
2. Obtain a session token.
3. Change account or role.
4. Reuse the old session token.
5. Access resources from the previous context.
6. Check if authorization is revalidated.

**Impact**
- Unauthorized access
- Privilege escalation
- Data exposure

---

## 14. Formula Injection in Calculations

**How it works:**  
User input included in price calculations without sanitization.

**Steps to Find**
1. Identify fields affecting price calculations.
2. Input mathematical expressions (e.g., `1+1`).
3. Attempt formula manipulation.
4. Test division by zero.
5. Inject negative multipliers.
6. Observe calculation results.

**Impact**
- Price manipulation
- Incorrect charges
- System errors

---

## 15. Bulk Discount Exploitation

**How it works:**  
Bulk discounts incorrectly applied or repeatedly reused.

**Steps to Find**
1. Identify discount thresholds.
2. Add items to reach threshold.
3. Apply discount.
4. Remove items below threshold.
5. Split orders to abuse discount.
6. Test if discount persists.

**Impact**
- Revenue loss
- Discount abuse

---

## 16. Account Enumeration via Logic Flaws

**How it works:**  
Different responses reveal valid accounts.

**Steps to Find**
1. Test login with valid username and wrong password.
2. Test login with invalid username.
3. Compare error messages.
4. Observe response timing differences.
5. Test password reset functionality.
6. Use timing attacks for enumeration.

**Impact**
- Information disclosure
- Targeted attacks
- Preparation for account takeover

---

## 17. Gift Card / Credit Abuse

**How it works:**  
Gift cards or credits applied multiple times.

**Steps to Find**
1. Obtain a valid gift card code.
2. Apply to one purchase.
3. Attempt applying the same code multiple times.
4. Test partial redemptions.
5. Check balance tracking.
6. Attempt negative balance scenarios.

**Impact**
- Financial fraud
- Revenue loss

---

## 18. Subscription Downgrade Abuse

**How it works:**  
Paid subscriptions downgraded while premium features remain accessible.

**Steps to Find**
1. Subscribe to premium plan.
2. Access premium features.
3. Downgrade to free plan.
4. Test if premium features still accessible.
5. Check permission revocation.
6. Verify feature flag updates.

**Impact**
- Revenue loss
- Unauthorized feature access

---

## 19. File Upload Quota Bypass

**How it works:**  
Upload limits enforced only client-side.

**Steps to Find**
1. Identify upload limits.
2. Upload files individually within limits.
3. Send concurrent upload requests.
4. Bypass client-side validation.
5. Check total storage usage.
6. Verify server-side enforcement.

**Impact**
- Resource exhaustion
- Increased storage costs
- Denial of service

---

## 20. Forced Browsing to Admin Functions

**How it works:**  
Administrative endpoints accessible without proper authorization.

**Steps to Find**
1. Map application endpoints.
2. Identify admin paths (`/admin`, `/dashboard`).
3. Access directly using low-privilege account.
4. Test various HTTP methods.
5. Check directory listings.
6. Verify authorization enforcement.

**Impact**
- System compromise
- Unauthorized admin access
- Data breach