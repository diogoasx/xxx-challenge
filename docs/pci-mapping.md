# PCI DSS v4.0 Mapping

This proof of concept is not intended to demonstrate full PCI DSS compliance.

The controls below show how the security design aligns with relevant PCI DSS principles and requirements.

| Security Control | PCI DSS v4.0 | Relationship |
| --- | --- | --- |
| Masked PAN in the Customer Operations flow | 3.4.1 | PAN is masked when displayed unless there is a legitimate business need to see additional digits. |
| Stored PAN protection in a production vault | 3.5.1 | Stored PAN must be rendered unreadable using an approved protection method. The clear-text PAN used in this PoC is fictional test data only. |
| Tool scoping and least privilege | 7.2.1 | Access is limited according to business need, job function and minimum required privileges. |
| Policy enforcement and prevention of business-logic abuse | 6.2.4 | Secure software engineering should mitigate common attacks, including attempts to abuse or bypass application functionality and access controls. |
| CHD access auditability | 10.2.1.1 | Individual access to cardholder data must be captured in audit logs. |
| Security event details | 10.2.2 | Audit events should contain sufficient information to identify who, what, when, where and how. |

## PCI Scope

The defended architecture attempts to minimize exposure of cardholder data by allowing the Customer Operations AI agent to receive only masked PAN data.

However, masking alone does not automatically make the application out of scope.

Systems that store, process or transmit CHD, have unrestricted connectivity to the CDE, or can impact the security of the CDE may remain in scope.

The final PCI DSS scope would therefore need to be validated with the organization's QSA based on the production architecture, connectivity and security responsibilities.

## Production Considerations

A production implementation would additionally require:

- protected storage of PAN;
- authenticated identities;
- role-based access control;
- authenticated human approval for privileged detokenization;
- enterprise secrets management;
- auditable CHD access;
- secure logging without full PAN exposure;
- network segmentation;
- monitoring and incident response.

The PoC demonstrates the security pattern, not full PCI DSS compliance.