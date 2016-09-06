import ROOT

class SpectrumQuantileFinder(object) :

  def __init__(self) :

    return

  def getFirstLastBinForQuantile(hist, desiredPercentage) :

  thisPercentage = 0
  thisInterval = 0
  remember1=1
  remember2=1
  smallestInterval= 1E5
  rememberThisPercentage=0
  initialIntegral = hist.Integral()
  for bin1 in range(0, hist.GetNbinsX()+2) :
    for bin2 in range(bin1, hist.GetNbinsX()+2) :
      thisPercentage = (hist.Integral(bin1,bin2))/initialIntegral
      thisInterval = hist.GetBinLowEdge(bin2) + hist.GetBinWidth(bin2) - hist.GetBinLowEdge(bin1)
      if (thisPercentage >= desiredPercentage) :
        if (thisInterval < smallestInterval) :
          remember1=bin1
          remember2=bin2
          smallestInterval=thisInterval
          rememberThisPercentage=thisPercentage
        break

  return [remember1,remember2]
