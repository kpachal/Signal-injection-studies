import sys
import ROOT
import argparse
import ConfigParser
import json
import math

from HistWrapper import WrappedHist

# Read command line arguments
# and get config file name
parser = argparse.ArgumentParser(description='Specify config and overwrite values if desired.')
parser.add_argument("--config",help = "Specify configuration file to use")
parser.add_argument("--seed",help="Input file (will overwrite config value)")
parser.add_argument("--sOverSqrtB",help="Output file (will overwrite config value)")
parser.add_argument("--masses",help="Masses to use: format as a list, eg [A.A, B.B, C.C]")
parser.add_argument("--widths",help="Widths to use: format as a list, eg [0.AA, 0.BB, 0.CC]")
args = parser.parse_args()

# Read configuration
configReader = ConfigParser.RawConfigParser()
configReader.read(args.config)
    
section = "IO"
inputBkgFile = configReader.get(section, "backgroundFileFormat")
inputBkgHistName = configReader.get(section,"backgroundHist")
signalFileFormat = configReader.get(section, "signalFileFormat")
signalHistName = configReader.get(section,"signalHist")
outputFileFormat = configReader.get(section,"outputFileFormat")

section = "General"
configmasses = json.loads(configReader.get(section,"masses"))
configwidths = json.loads(configReader.get(section,"widths"))

if args.masses :
  theseMasses = json.loads(args.masses)
else :
  theseMasses = configmasses

if args.widths :
  theseWidths = json.loads(args.widths)
else :
  theseWidths = configwidths

# Get and store histograms
backgroundfile = ROOT.TFile(inputBkgFile,"READ")
basicBkgHist = backgroundfile.Get(inputBkgHistName)
basicBkgHist.SetName("myBackground")
basicBkgHist.SetDirectory(0)
backgroundfile.Close()

for mass in theseMasses :
  for width in theseWidths :

    signalFileName = signalFileFormat.format(int(mass),int(100*width))
    signalfile = ROOT.TFile(signalFileName,"READ")
    signalTemplateHist = signalfile.Get(signalHistName)
    signalTemplateHist.SetDirectory(0)
    signalfile.Close()

    signalWrapper = WrappedHist(signalTemplateHist)
    firstSigBin = signalWrapper.firstBinWithData
    lastSigBin = signalWrapper.lastBinWithData
    currentNorm = signalTemplateHist.Integral()

    correspondingDataNorm = basicBkgHist.Integral(firstSigBin,lastSigBin)

    scaleNeeded = float(args.sOverSqrtB)*math.sqrt(correspondingDataNorm)/currentNorm
    print "Using scale " , scaleNeeded

    # Set uncertainties to be sqrt(bin content)
    signalTemplateHist.Scale(scaleNeeded)
    for bin in range(0, signalTemplateHist.GetNbinsX()+2) :
      if (signalTemplateHist.GetBinContent(bin) < 1.0) : signalTemplateHist.SetBinContent(bin,0.0)
      signalTemplateHist.SetBinError(bin,math.sqrt(signalTemplateHist.GetBinContent(bin)))

    borderlineHist = ROOT.TH1D(basicBkgHist)
    borderlineHist.Sumw2()
    borderlineHist.SetDirectory(0)
    borderlineHist.SetName("combinedHist")
    borderlineHist.Add(signalTemplateHist)

    print "In mass, width",mass,width

    outputHistFileName = outputFileFormat.format(mass,
           int(width*100),int(eval(args.sOverSqrtB)*10))
    print "making file",outputHistFileName
    outputHistFile = ROOT.TFile(outputHistFileName,"RECREATE")
    outputHistFile.cd()
    borderlineHist.Write("PseudoDataWithSig")
    outputHistFile.Close()

