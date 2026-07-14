"""Support behavior of the local curved auxiliary canonical transformation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalSupportCertificate:
    entries: tuple[tuple[str, int, str], ...]

    @staticmethod
    def build() -> "LocalSupportCertificate":
        result = LocalSupportCertificate(
            entries=(
                ("D_h[A_g^{-1}G^b]", 2, "finite differential"),
                ("D_v[A_g^{-1}G^b]", 1, "finite differential"),
                ("A_g^{-1}", 0, "pointwise bundle inverse"),
                ("eta=xi_0-d sigma", 1, "finite differential"),
                ("formal cotangent lifts", 2, "finite formal adjoints"),
                ("universal auxiliary homotopy", 0, "pointwise bundle map"),
            )
        )
        result.verify()
        return result

    def verify(self) -> None:
        if any(order < 0 for _, order, _ in self.entries):
            raise AssertionError("a nonlocal support-changing entry was admitted")
        if any("Green" in kind or "projector" in kind for _, _, kind in self.entries):
            raise AssertionError("support certificate contains a nonlocal operation")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-retract-support-v1",
            "operators": [
                {"name": name, "differential_order": order, "kind": kind}
                for name, order, kind in self.entries
            ],
            "compact_support_preserved": True,
            "spacelike_compact_support_preserved": True,
            "smooth_global_support_preserved": True,
            "support_statement": "supp(Tu) subseteq supp(u)",
            "uses_Green_operator": False,
            "uses_nonlocal_projector": False,
            "guard": (
                "support preservation is exact for the displayed local maps but "
                "does not prove their still-open curved chain-map identities"
            ),
        }
