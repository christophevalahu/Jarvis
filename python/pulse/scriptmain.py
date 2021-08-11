from pulsesequences import *
from states import *


# ------ Edit These Parameters ------
state = "D1ms"
detuning = -2.5
step = 0.5
nsteps = 11
nruns = 100
# -----------------------------------
delay = 0
sb_cool = False
# -----------------------------------

# ------ Uncomment desired function ----------
#statedetone(state = state, steps = 1, runs = nruns,sb_cool=sb_cool)
#statedettwo(nsteps, nruns, sb_cool=sb_cool)
#statedetmatch(nsteps, nruns)

freqscan(state, detuning, step, nsteps, nruns, sb_cool=sb_cool, delay=delay)
#timescan(state, detuning, step, nsteps, nruns, sb_cool = sb_cool)
#timescan_pf(state, detuning, step, nsteps, nruns, sb_cool = sb_cool)

#optimizeSBcooling(detuning, step, nsteps, nruns)
#secfreq("COM", detuning, step, nsteps, nruns, amp = 120)
#coherencetime(state, detuning, step, nsteps, nruns, delay, sb_cool = sb_cool)
#coherencetimemotion(state, detuning, step, nsteps, nruns, delay, sb_cool = sb_cool)
#lifetime(state, detuning, step, nsteps, nruns, delay)
#dopplertemp(state, detuning, step, nsteps, nruns)
#spinlocking(state, detuning, step, nsteps, nruns)
#sensing(state, detuning, step, nsteps, nruns)

#amplitude_noise_reconstruction(state, nsteps, nruns, iteration = 9, basis = 'Y')

#cddsbfreq(state, detuning, step, nsteps, nruns, sb_cool = sb_cool) 
#cddgate(state, detuning, step, nsteps, nruns, sb_cool = sb_cool) 
#sk1pulse(state, steps = nsteps, runs = nruns)

#cddgatefreq('sym', detuning, step, nsteps, nruns, sb_cool)
#cddcartimescan(state, detuning, step, nsteps, nruns) 
#cddgatecar(det = detuning, step = step, steps = nsteps, runs = nruns, ion = '0')

#spinspingate(detuning, step, nsteps, nruns)
#spinspinfreq(state, detuning, step, nsteps, nruns)
#spinspintime(state = state, mode = "both", det = detuning, step = step, steps = nsteps, runs = nruns)

#catfreqscan("SYM1", detuning, step, nsteps, nruns, sb_cool)
#cattimescan("ION1", detuning, step, nsteps, nruns, sb_cool)
#msgate(detuning, step, nsteps, nruns)
#mstwotonegate(detuning, step, nsteps, nruns)
#msparity(detuning, step, nsteps, nruns)
#msparity01(detuning,step,nsteps,nruns)
#msRFpower(state = state, det = detuning, step = step, steps = nsteps, runs = nruns)
#msdetscan("SYM", 1, detuning, step, nsteps, nruns)
#mssscoupling(state, detuning, step, nsteps, nruns)
#msparitydetscan(mode = "SYM", det = detuning, step = step, steps = nsteps, runs = nruns)
#msMWpowermatch(state, detuning, step, nsteps, nruns, delay)
#msMWpowermatchboth(state, detuning, step, nsteps, nruns, delay)
#CNOTphase(nsteps, nruns)
#RLtest(det = 0, step = 0, steps = nsteps, runs = nruns)
#spanishgate(detuning, step, nsteps, nruns)

#RLcircuitX0X1(GS_STATE_PARAM, GS_SUBSPACE_PARAM, steps = nsteps, runs = nruns)
# ---------------------------