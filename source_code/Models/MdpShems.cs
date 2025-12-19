using System.Collections.Generic;

namespace DynStabSpace;

public class MdpShems
{
	public string ShemeName;

	public bool IsReady;

	public bool IsStable;

	public double MaxStep;

	public double Ppred;

	public double Pstart;

	public List<MdpEvents> Events;
}
