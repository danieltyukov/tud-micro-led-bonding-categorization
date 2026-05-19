**Subject:** Re: micro-LED test PCB — switching to bare PCB (no assembly)

---

Hi Filip,

Thanks for digging in. Let's drop the assembly side entirely and just order **bare PCBs** instead — that'll skip the unassigned-parts back-and-forth and is genuinely faster overall.

The non-LED components on this board are 4 × NTC (0402), 1 × thin-film resistor (0603), and 64 × pin header pins (2.54 mm THT). That's roughly 15 minutes of hand soldering at EKL on the way to bonding the LEDs — quicker than fighting the BOM editor at either fab.

**Proposed Aisler order:**
- Service: **Beautiful Boards** (bare PCB, no assembly)
- 3 boards
- 2-layer FR-4, **1.6 mm thickness**
- **ENIG finish (mandatory — the LED bond lands and probe pads must be gold)**
- White silkscreen
- **Express / Blitz Service** if available, so they land this week
- I went into the Aisler project just now and switched the surface finish from HASL to ENIG (it had defaulted to HASL) — everything else in the project NVKFPETD is already correct

The project should now be ready to check out on the Beautiful Boards path. Expected cost is around €30-50 for 3 boards. Ahmed will send you the project code for billing.

This skips the assembly side completely, so no BOM, no DNP flags, no part assignment, and no risk of Aisler picking up phantom capacitor MPNs for our DoE bond pads. I'll handle the SMD soldering at EKL while I'm in there for the LED bonding.

Let me know if you need anything else from my side.

Best,

Daniel
