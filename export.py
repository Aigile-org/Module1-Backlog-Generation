def remove_lines_and_save(text, output_file):
    cleaned_text = text.replace("\n", " ")  # Replace newlines with spaces
    # Write the cleaned text to a new file
    with open(output_file, "w") as file:
        file.write(cleaned_text)

# Example usage:
text = """Here’s a detailed extraction of the requirements and all relevant details from the document:

### **Project Title: Central Trading System**

#### **Project Overview**
The Central Trading System (CTS) is designed to facilitate electronic trading by integrating various market participants into a single platform. The system automates order matching, trade execution, and market data dissemination while ensuring regulatory compliance and operational efficiency.

---

### **System Requirements**
#### **1. Functional Requirements**
- **Order Management:**
  - Support for multiple order types (market, limit, stop-loss, etc.).
  - Order placement, modification, and cancellation features.
  - Validation of orders against user account balance and trading limits.

- **Trade Execution:**
  - Matching of buy and sell orders based on price and time priority.
  - Partial order fulfillment capability.
  - Automatic execution of trades with immediate confirmation.

- **Market Data Handling:**
  - Real-time dissemination of trade data (price, volume, order book).
  - Subscription-based feeds for users to receive live updates.
  - Historical trade data storage for analysis and reporting.

- **User Authentication and Authorization:**
  - Secure login mechanism with multi-factor authentication.
  - Role-based access control (traders, brokers, regulators).
  - Encryption of sensitive user information.

- **Regulatory Compliance:**
  - Trade logging for audit trails.
  - Compliance with financial regulations (e.g., anti-money laundering).
  - Reporting mechanisms for suspicious transactions.

- **Risk Management:**
  - Exposure limits on individual traders and institutions.
  - Circuit breakers for market stability.
  - Pre-trade and post-trade risk analysis.

- **Account and Portfolio Management:**
  - Real-time tracking of holdings, gains/losses.
  - Account funding and withdrawal options.
  - Integration with banking and settlement systems.

- **Notification System:**
  - Alerts for executed trades, margin calls, and account activity.
  - Configurable notifications via email, SMS, or in-app alerts.

---

#### **2. Non-Functional Requirements**
- **Performance:**
  - Low-latency execution to support high-frequency trading.
  - Scalability to handle peak trading volumes.

- **Security:**
  - End-to-end encryption for data in transit and at rest.
  - Secure APIs for third-party integrations.

- **Availability and Reliability:**
  - 99.99% uptime with failover mechanisms.
  - Redundant architecture for fault tolerance.

- **Usability:**
  - Intuitive UI/UX for traders and brokers.
  - Support for multiple languages.

- **Extensibility:**
  - Modular design allowing easy addition of new asset classes.
  - API support for external trading algorithms.

---

### **Technical Specifications**
- **Architecture:**
  - Microservices-based deployment.
  - Event-driven communication model.
  - Load-balanced infrastructure.

- **Technology Stack:**
  - Backend: Java/C++ for core trading engine.
  - Frontend: React/Angular for web interface.
  - Database: PostgreSQL/NoSQL for storing market data.
  - Messaging: Kafka/RabbitMQ for real-time data streams.

- **Deployment and Hosting:**
  - Cloud-based deployment (AWS/Azure/GCP).
  - Kubernetes for container orchestration.
  - CI/CD pipelines for continuous deployment.

---

### **Additional Considerations**
- **Integration with External Systems:**
  - Connection to stock exchanges and liquidity providers.
  - API for brokerage firms to place orders programmatically.

- **Testing and Quality Assurance:**
  - Unit, integration, and stress testing.
  - Simulated trading environments for testing strategies.

- **Legal and Compliance Aspects:**
  - GDPR and financial market regulations adherence.
  - Secure storage of transaction logs for audits.

---

"""

output_filename = "filtered_text.txt"

remove_lines_and_save(text, output_filename)
print(f"Filtered text saved to {output_filename}")
