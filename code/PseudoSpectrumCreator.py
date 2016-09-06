import ROOT
import math

class PseudoSpectrumCreator(object) :

  def __init__(self,seed=6789) :

    ROOT.gRandom = ROOT.TRandom3(seed)
    ROOT.gRandom.SetSeed(seed)
    self.randomNumberGenerator = ROOT.TRandom3(seed)
    

  def generatePseudoSpectrumFromHist(self,baseHistogram, currentLumi, desiredLumi) :

    finalHist = ROOT.TH1D(baseHistogram)
    finalHist.Reset()
    finalHist.SetDirectory(0)
    finalHist.SetName("pseudospec_{0}_{1}lumi".format(baseHistogram.GetName(),desiredLumi))

    for bin in range(0,finalHist.GetNbinsX()+2) :

      initialExp = (desiredLumi/currentLumi)*baseHistogram.GetBinContent(bin)
      pseudo = self.randomNumberGenerator.Poisson(initialExp)
      finalHist.SetBinContent(bin,pseudo)
      finalHist.SetBinError(bin,math.sqrt(pseudo))

    return finalHist

  def generatePseudoSpectrumFromFunction(self,baseHistogram, baseFunction, currentLumi, desiredLumi, lowEdge, highEdge) :
  
    finalHist = ROOT.TH1D(baseHistogram)
    finalHist.Reset()
    finalHist.SetDirectory(0)
    finalHist.SetName("pseudospec_{0}_{1}lumi".format(baseHistogram.GetName(),desiredLumi))

    # Fill random into now empty histogram
    # until integral equals total integral of function we wanted.
    numToGenerate = baseFunction.Integral(lowEdge,highEdge)*desiredLumi/currentLumi

    finalHist.FillRandom(baseFunction.GetName(),numToGenerate)

    return finalHist