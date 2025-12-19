using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Linq;
using rst_operations;

namespace DynStabSpace;

public class UostStabilityCalc
{
	private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Uост на границе устойчивости";

	private BackgroundWorker _w;

	private ObservableCollection<RgmsInfo> RgmsInfo;

	private ObservableCollection<ScnsInfo> ScnsInfo;

	private List<VrnInfo> VrnInf;

	private FileInfo Rems;

	private List<KprInfo> KprInf;

	public string root => tmp_root;

	public int Max => RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() + 1;

	public UostStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, List<KprInfo> kprs)
	{
		if (rgms.Count() == 0 || scns.Count() == 0)
		{
			throw new InitialDataException("Не заданы все исходные данные для определения остаточного напряжения на шинах энергообъекта при КЗ на границе устойчивости!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}{Environment.NewLine}");
		}
		RgmsInfo = rgms;
		ScnsInfo = scns;
		VrnInf = vrns;
		Rems = rems;
		KprInf = kprs;
		_w = sender as BackgroundWorker;
		Directory.CreateDirectory(tmp_root);
	}

	public List<UostResults> Calc()
	{
		int num = 0;
		List<UostResults> list = new List<UostResults>();
		int num2 = 1;
		foreach (RgmsInfo item in RgmsInfo)
		{
			List<UostShems> list2 = new List<UostShems>();
			foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
			{
				bool flag = false;
				List<UostEvents> list3 = new List<UostEvents>();
				foreach (ScnsInfo item3 in ScnsInfo)
				{
					RastrOperations rastrOperations = new RastrOperations();
					rastrOperations.Load(item.Name);
					rastrOperations.DynSettings();
					flag = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
					if (!flag)
					{
						continue;
					}
					rastrOperations.Load(item3.Name);
					double distance = 100.0;
					string text = "";
					int num3 = 0;
					double time_start = 0.0;
					double num4 = -1.0;
					double num5 = -1.0;
					int r_id = 0;
					int x_id = 0;
					foreach (int item4 in rastrOperations.Selection("DFWAutoActionScn"))
					{
						if (rastrOperations.getVal("DFWAutoActionScn", "ObjectClass", item4) == "vetv")
						{
							text = rastrOperations.getVal("DFWAutoActionScn", "ObjectKey", item4);
							rastrOperations.setVal("DFWAutoActionScn", "State", item4, 1);
						}
						if (rastrOperations.getVal("DFWAutoActionScn", "ObjectClass", item4) == "node")
						{
							num3 = Convert.ToInt32(rastrOperations.getVal("DFWAutoActionScn", "ObjectKey", item4));
							time_start = rastrOperations.getVal("DFWAutoActionScn", "TimeStart", item4);
							rastrOperations.setVal("DFWAutoActionScn", "ObjectKey", item4, num2);
							if (rastrOperations.getVal("DFWAutoActionScn", "ObjectProp", item4) == "r")
							{
								num4 = Convert.ToDouble(rastrOperations.getVal("DFWAutoActionScn", "Formula", item4).Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator));
								r_id = item4;
							}
							if (rastrOperations.getVal("DFWAutoActionScn", "ObjectProp", item4) == "x")
							{
								num5 = Convert.ToDouble(rastrOperations.getVal("DFWAutoActionScn", "Formula", item4).Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator));
								x_id = item4;
							}
						}
					}
					double num6 = ((num4 == -1.0) ? (Math.PI / 2.0) : Math.Atan(num5 / num4));
					double num7 = Math.Sqrt(((num4 != -1.0) ? Math.Pow(num4, 2.0) : 0.0) + Math.Pow(num5, 2.0));
					int num8 = Convert.ToInt32(text.Split(new char[1] { ',' })[0]);
					int num9 = Convert.ToInt32(text.Split(new char[1] { ',' })[1]);
					int num10 = Convert.ToInt32(text.Split(new char[1] { ',' })[2]);
					double num11 = ((num8 == num3) ? 0.1 : 99.9);
					double num12 = 100.0 - num11;
					double r = rastrOperations.getVal("vetv", "r", $"ip = {num8} & iq = {num9} & np = {num10}");
					double x = rastrOperations.getVal("vetv", "x", $"ip = {num8} & iq = {num9} & np = {num10}");
					double num13 = rastrOperations.getVal("vetv", "b", $"ip = {num8} & iq = {num9} & np = {num10}");
					rastrOperations.setVal("vetv", "sta", $"ip = {num8} & iq = {num9} & np = {num10}", 1);
					rastrOperations.setVal("node", "bsh", $"ny = {num8}", num13 / 2.0);
					rastrOperations.setVal("node", "bsh", $"ny = {num9}", num13 / 2.0);
					int num14 = rastrOperations.AddTableRow("node");
					rastrOperations.setVal("node", "ny", num14, num2);
					rastrOperations.setVal("node", "uhom", num14, rastrOperations.getVal("node", "uhom", $"ny = {num3}"));
					int num15 = rastrOperations.AddTableRow("vetv");
					int num16 = rastrOperations.AddTableRow("vetv");
					rastrOperations.setVal("vetv", "ip", num15, num8);
					rastrOperations.setVal("vetv", "iq", num15, num2);
					rastrOperations.setVal("vetv", "ip", num16, num2);
					rastrOperations.setVal("vetv", "iq", num16, num9);
					rastrOperations.rgm();
					rastrOperations.SetLineForUostCalc(num15, num16, r, x, num11);
					DynamicResult dynamicResult = rastrOperations.RunDynamic(_ems: true);
					rastrOperations.SetLineForUostCalc(num15, num16, r, x, num12);
					DynamicResult dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
					if (dynamicResult.IsSuccess && dynamicResult2.IsSuccess && (dynamicResult.IsStable ^ dynamicResult2.IsStable))
					{
						double num17 = (dynamicResult.IsStable ? num11 : num12);
						double num18 = (dynamicResult.IsStable ? num12 : num11);
						double num19 = Math.Abs(num17 - num18) * 0.5;
						rastrOperations.SetLineForUostCalc(num15, num16, r, x, num19);
						DynamicResult dynamicResult3 = rastrOperations.RunDynamic(_ems: true);
						while (dynamicResult3.IsSuccess && (!dynamicResult3.IsStable || Math.Abs(num17 - num18) > 0.5))
						{
							if (dynamicResult3.IsStable)
							{
								num17 = num19;
							}
							else
							{
								num18 = num19;
							}
							num19 += Math.Abs(num18 - num17) * 0.5 * (double)(((dynamicResult.IsStable && dynamicResult3.IsStable) || (!dynamicResult.IsStable && !dynamicResult3.IsStable)) ? 1 : (-1));
							distance = num19;
							rastrOperations.SetLineForUostCalc(num15, num16, r, x, num19);
							dynamicResult3 = rastrOperations.RunDynamic(_ems: true);
						}
					}
					else if (dynamicResult.IsSuccess && !dynamicResult.IsStable && dynamicResult2.IsSuccess && !dynamicResult.IsStable)
					{
						distance = -1.0;
						rastrOperations.SetLineForUostCalc(num15, num16, r, x, (num8 == num3) ? 99.9 : 0.1);
						double num20 = ((num7 > 0.1) ? (num7 * 2.0) : 1.0);
						double num21 = num7;
						if (num4 == -1.0)
						{
							rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6));
						}
						else
						{
							rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6), r_id, num20 * Math.Cos(num6));
						}
						DynamicResult dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
						while (dynamicResult4.IsSuccess && !dynamicResult4.IsStable)
						{
							num21 = num20;
							num20 += ((num7 > 0.1) ? num7 : 1.0);
							if (num4 == -1.0)
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6));
							}
							else
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6), r_id, num20 * Math.Cos(num6));
							}
							dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
						}
						while (dynamicResult4.IsSuccess && (!dynamicResult4.IsStable || 1.0 - num21 / num20 > 0.025))
						{
							double num22 = (dynamicResult4.IsStable ? ((num21 - num20) * 0.5) : ((num20 - num21) * 0.5));
							double num23 = num20 + num22;
							if (num4 == -1.0)
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num23 * Math.Sin(num6));
							}
							else
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num23 * Math.Sin(num6), r_id, num23 * Math.Cos(num6));
							}
							dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
							if (dynamicResult4.IsStable)
							{
								num20 = num23;
							}
							else
							{
								num21 = num23;
							}
						}
					}
					List<Values> list4 = new List<Values>();
					double beginUost = -1.0;
					double endUost = -1.0;
					DynamicResult dynamicResult5 = rastrOperations.RunDynamic(_ems: false, time_start + 0.02);
					if (dynamicResult5.IsSuccess && dynamicResult5.IsStable)
					{
						beginUost = (from k in rastrOperations.GetPointsFromExitFile("node", "vras", $"ny = {num8}")
							where k.X == time_start
							select k).FirstOrDefault().Y;
						endUost = (from k in rastrOperations.GetPointsFromExitFile("node", "vras", $"ny = {num9}")
							where k.X == time_start
							select k).FirstOrDefault().Y;
					}
					foreach (KprInfo item5 in KprInf)
					{
						list4.Add(new Values
						{
							Id = item5.Id,
							Name = item5.Name,
							Value = rastrOperations.getVal(item5.Table, item5.Col, item5.Selection)
						});
					}
					list3.Add(new UostEvents
					{
						Name = item3.name,
						Values = list4,
						BeginNode = num8,
						EndNode = num9,
						Np = num10,
						BeginUost = beginUost,
						EndUost = endUost,
						Distance = distance
					});
					num++;
					_w.ReportProgress(num);
				}
				list2.Add(new UostShems
				{
					ShemeName = item2.Name,
					IsStable = flag,
					Events = list3
				});
			}
			list.Add(new UostResults
			{
				RgName = item.name,
				UostShems = list2
			});
		}
		return list;
	}
}
