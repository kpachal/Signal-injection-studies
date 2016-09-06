python -m scripts.createBWSignals --config configurations/makeBWSignals.ini
python -m scripts.generateBkgPseudodata_fromHist --config configurations/makeBackgrounds_EOYE.ini --tag EOYE
python -m scripts.generateSigPlusBkg.py --config configurations/makeSigPlusBkg_EOYE.ini --sOverSqrtB 3


python -m SearchPhase --config configurations/SearchPhase_PEWithSignal_EOYE.ini --file signal_and_bkg/SignalAndBackground_mass3000_width15_strength60.root --outputfile test.root
