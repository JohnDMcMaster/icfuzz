# icfuzz

Rough scripts I use for brute force style security investigations

Mostly intended to use a programmer like minipro or BP Microsystems and repeatedly query chip status

Some modes use linear stage to scan around, others just loop and expect user to manually adjust glitch source

Supported glitch sources:
  * Passive (ex: a laser that is always on)
  * ezlaze

# Laser fuzzing


