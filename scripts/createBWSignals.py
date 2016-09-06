import ROOT
import argparse
import ConfigParser
import json

# Get config file name
parser = argparse.ArgumentParser(description='Specify config and overwrite values if desired.')
parser.add_argument("--config",help = "Specify configuration file to use")
parser.add_argument("--tag",help="Tag to add to all directory names to separate this production")
args = parser.parse_args()

# Read configuration
defaults = {    "widths": "[0.07,0.10,0.15]",
                "startPoints": 200,
                "stopDensePoints": 2000,
                "stopMediumPoints": 3000,
                "stopPoints" : 7500,
                "binnings": "[0]"}

configReader = ConfigParser.RawConfigParser(defaults)
configReader.read(args.config)
    
section = "IO"
inputBkgFile = configReader.get(section, "inputFileName")
inputBkgHistName = configReader.get(section,"binTemplateHist")
outputFileFormat = configReader.get(section, "outputFileFormat")
    
section = "MassesAndWidths"
widths = json.loads(configReader.get(section,"widths"))
nWidths = len(widths)
startPoints = configReader.getint(section,"startPoints")
stopDensePoints = configReader.getint(section,"stopDensePoints")
stopMediumPoints = configReader.getint(section,"stopMediumPoints")
stopPoints = configReader.getint(section,"stopPoints")

section = "Binnings"
binnings = json.loads(configReader.get(section,"binnings"))
nBinnings = len(binnings)

# Get histogram to use as template
infile = ROOT.TFile(inputBkgFile,"READ")
nominalBkg = infile.Get(inputBkgHistName)
nominalBkg.SetDirectory(0)
infile.Close()

# Generate list of masses from given info
masses = []
for mass in range(startPoints, stopDensePoints, 50) : masses.append(float(mass))
for mass in range(stopDensePoints, stopMediumPoints, 100) : masses.append(float(mass))
for mass in range(stopMediumPoints, stopPoints, 200) : masses.append(float(mass))

# Generate signals
for mass in masses :
  for width in widths :
  
    widthForName = int(width*100)
    onesigma = mass*width
    filename = outputFileFormat.format(int(mass),widthForName)

    # Generate BW
    GenericBW = ROOT.TF1("signal","TMath::BreitWigner(x,{0},{1})".format(mass,onesigma),0,13000)
    outfile = ROOT.TFile(filename,"RECREATE")

    for binning in binnings :

      # Convert to histogram
      
      low = nominalBkg.GetBinLowEdge(1)
      high = nominalBkg.GetBinLowEdge(nominalBkg.GetNbinsX()) + nominalBkg.GetBinWidth(nominalBkg.GetNbinsX())

      if binning==0 :
        SignalHist = ROOT.TH1D(nominalBkg)
        SignalHist.SetName("nominalBins")
        SignalHist.SetTitle("nominalBins")
      elif binning < 0 and binning > -1.5 :
        newBins = []
        for j in range(0, nominalBkg.GetNbinsX()+1) :
          newBins.append(nominalBkg.GetBinLowEdge(j))
          newBins.append(nominalBkg.GetBinLowEdge(j)+nominalBkg.GetBinWidth(j)/2.0)
        newBins.append(nominalBkg.GetBinLowEdge(nominalBkg.GetNbinsX())+nominalBkg.GetBinWidth(nominalBkg.GetNbinsX()))
        SignalHist = ROOT.TH1D("halfNominalBins","halfNominalBins",len(newBins),array(newBins))
      elif binning < -1 and binning > -99 :
        SignalHist = ROOT.TH1D(nominalBkg)
        SignalHist.Rebin(int(-1*binning))
        SignalHist.SetName("{0}TimesNominalBins".format(int(-1*binning)))
        SignalHist.SetTitle("{0}TimesNominalBins".format(int(-1*binning)))
      elif (binning < -99) :
        newBins = []
        for j in range(0, nominalBkg.GetNbinsX()) :
          newBins.append(nominalBkg.GetBinLowEdge(j+1)+50)
        newBins.append(nominalBkg.GetBinLowEdge(nominalBkg.GetNbinsX())+nominalBkg.GetBinWidth(nominalBkg.GetNbinsX())+50)
        SignalHist = ROOT.TH1D("shifted50NominalBins","shifted50NominalBins",nominalBkg.GetNbinsX(),array(newBins))
      else :
        nBins = int((high - low)/ float(binning))
        SignalHist = ROOT.TH1D("binsCloseTo{0}".format(binning),"binsCloseTo{0}".format(binning),nBins,low,high)

      # Make sure histograms are clear and free, regardless
      SignalHist.Reset()
      SignalHist.SetDirectory(0)

      for bin in range(0, SignalHist.GetNbinsX()+2) :
        a = SignalHist.GetBinLowEdge(bin)
        b = SignalHist.GetBinLowEdge(bin)+SignalHist.GetBinWidth(bin)
        content = GenericBW.Integral(a,b)
        SignalHist.SetBinContent(bin,content)
        SignalHist.SetBinError(bin,0.)

      intNow = SignalHist.Integral()

      thisPercentage = 0
      thisInterval = 0
      remember1 = 1
      remember2 = 1
      smallestInterval = 1E6
      rememberThisPercentage = 0
      for bin1 in range(0,SignalHist.GetNbinsX()+2) :
        for bin2 in range(bin1,SignalHist.GetNbinsX()+2) :
          thisPercentage = (SignalHist.Integral(bin1,bin2))/intNow;
          thisInterval = SignalHist.GetBinLowEdge(bin2) + SignalHist.GetBinWidth(bin2) - SignalHist.GetBinLowEdge(bin1)
          if (thisPercentage >= 0.95) :
            if (thisInterval < smallestInterval) :
              remember1=bin1
              remember2=bin2
              smallestInterval=thisInterval
              rememberThisPercentage=thisPercentage
            break
 
      for bin in range(0, SignalHist.GetNbinsX()+2) :
        if (bin < remember1) or (bin > remember2) :
          SignalHist.SetBinContent(bin,0.)
          SignalHist.SetBinError(bin,0.)
      intNow = SignalHist.Integral()
      SignalHist.Scale(1.0/intNow)

      outfile.cd()
      SignalHist.Write()

    outfile.Close()

