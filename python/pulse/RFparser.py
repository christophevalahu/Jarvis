'''
    Author : Christophe Valahu and apprentice
    Last Modified : 15/04/19
    File : RFparser.py
    
    Description : Parse rf pulses for AWG

'''

def _rf_shaped_pulse_str(pulse):
    lines = "shapedPulse %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'])
    for chan in pulse['chans']:
    	lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['freq'], chan['freq step'], chan['phase'], chan['phase step'])
    return lines

def _rf_reset_phase(pulse):
    lines = "resetPhase %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'])
    for chan in pulse['chans']:
    	lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s\n" % \
        (0, 0, 0, 0, 0, 0)
    return lines

def _rf_mod_pulse_str(pulse):
    lines = "modPulse %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['omega'], chan['omega step'], chan['phi'], chan['phi step'], chan['b'], chan['b step'], chan['nu'], chan['nu step'], chan['theta'], chan['theta step'])
    return lines

def _rf_mapping_pulse_str(pulse):
    lines = "mappingPulse %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines

def _rf_stark_sine_pulse_str(pulse):
    lines = "starkSinePulse %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines

def _rf_blackmann_pulse_str(pulse):
    lines = "blackmanPulse %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines

def _rf_mapping_pulse_cut_str(pulse):
    lines = "mappingPulseCut %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines

def _rf_mapping_pulse_cut_end_str(pulse):
    lines = "mappingPulseCutEnd %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines


def _rf_mapping_pulse_flip_str(pulse):
    lines = "mappingPulseFlip %s\n" % (len(pulse['chans'])+2)
    lines += "%s\nTime: %s Step: %s IQ: %s Chans: %s TimingArray: %s,%s\n" % \
    (pulse['string'], pulse['time'], pulse['step'], pulse['IQ'], len(pulse['chans']), pulse['timeps'], pulse['timechirp'])
    for chan in pulse['chans']:
        lines += " amp: %s amp step: %s channelArray: %s,%s,%s,%s,%s,%s\n" % \
        (chan['amp'], chan['amp step'], chan['initial freq'], chan['initial freq step'], chan['final freq'], chan['final freq step'], chan['phase'], chan['phase step'])
    return lines
    
def _rf_pulse_text(pulse):

    pulseType = pulse['type']
    if pulseType == 'shapedPulse':
        return _rf_shaped_pulse_str(pulse)
    elif pulseType == 'resetPhase':
        return _rf_reset_phase(pulse)
    elif pulseType == 'modPulse':
        return _rf_mod_pulse_str(pulse)
    elif pulseType == 'mappingPulse':
        return _rf_mapping_pulse_str(pulse)
    elif pulseType == 'starkSinePulse':
        return _rf_stark_sine_pulse_str(pulse)
    elif pulseType == 'blackmanPulse':
        return _rf_blackmann_pulse_str(pulse)
    elif pulseType == 'mappingPulseCut':
        return _rf_mapping_pulse_cut_str(pulse)
    elif pulseType == 'mappingPulseCutEnd':
        return _rf_mapping_pulse_cut_end_str(pulse)
    elif pulseType == 'mappingPulseFlip':
        return _rf_mapping_pulse_flip_str(pulse)
    else:
        return ''
        

    
def makeRFPulseString(RFPulseList) :

    RFTextOut = ""
    
    for RFPulse in RFPulseList :
        RFTextOut += _rf_pulse_text(RFPulse)
    
    return RFTextOut
    
    