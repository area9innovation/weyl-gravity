# Panelwise complex-ball transport shortfall

Sixteen outward-rounded frequency panels cover the proposed QNM contour.
On every panel, an order-16 Taylor method with step \(1/4\) and a rigorous
Cauchy remainder transports the coarse ECS spin-two initializer to \(r=4\).

Although the rail recenters after each step, plain rectangular interval
dependency grows to at least order \(10^{16}\).  It is much sharper than the
global \(10^{33}\) Gronwall ball but still unusable for Evans nonvanishing.

The next implementation must preserve affine correlations through Lohner
reconditioning or propagate the projective Riccati/Grassmannian datum.
