import sys
import ROOT
import argparse
import ConfigParser
import json

from code.PseudoSpectrumCreator import PseudoSpectrumCreator

# Read command line arguments
parser = argparse.ArgumentParser(description='Specify config and overwrite values if desired.')
parser.add_argument("--config",help = "Specify configuration file to use")
parser.add_argument("--seed",help="Use specific random number seed")
parser.add_argument("--tag",help="Use ")
args = parser.parse_args()

# Read configuration
configReader = ConfigParser.RawConfigParser()
configReader.read(args.config)
    
section = "IO"
inputBkgFile = configReader.get(section, "backgroundFile")
inputBkgHistName = configReader.get(section, "backgroundHist")
outputFileFormat = configReader.get(section, "outputFileFormat")

section = "General"
initialLumi = configReader.getfloat(section,"initialLumi")
lumis = json.loads(configReader.get(section,"lumis"))
nLumis = len(lumis)

# Open files and retrieve background, set up to use
infile = ROOT.TFile(inputBkgFile,"READ")
nominalBkg = infile.Get(inputBkgHistName)
nominalBkg.SetDirectory(0)

if args.seed :
  myPEMaker = PseudoSpectrumCreator(eval(args.seed))
else :
  myPEMaker = PseudoSpectrumCreator()

for lumi in lumis :

    thislumihist = myPEMaker.generatePseudoSpectrumFromHist(nominalBkg, initialLumi, lumi)
    thislumihist.SetDirectory(0)

    outputname = outputFileFormat.format(args.tag,args.seed,"{0}".format(lumi).replace(".","p"))
    print "Output file name: ", outputname
    outfile = ROOT.TFile(outputname,"RECREATE")
    outfile.cd()
    thislumihist.Write(thislumihist.GetName().replace(".","p"))
    outfile.Close()
