using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using rst_operations;

namespace DynStabSpace;

public class Shunt_KZ
{
	private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Шунты КЗ";

	private double BaseAngle = 1.471;

	private BackgroundWorker _w;

	private ObservableCollection<RgmsInfo> RgmsInfo;

	private List<VrnInfo> VrnInf;

	private FileInfo Rems;

	private List<ShuntKZ> ShuntKZInf;

	private bool UseSelNodes;

	private bool UseTypeValU;

	private bool CalcOnePhase;

	private bool CalcTwoPhase;

	public string root => tmp_root;

	public int Max
	{
		get
		{
			int num = 0;
			int num2 = (CalcOnePhase ? 1 : 0) + (CalcTwoPhase ? 1 : 0);
			if (!UseSelNodes)
			{
				num = RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ShuntKZInf.Count() * num2;
			}
			else
			{
				RastrOperations rastrOperations = new RastrOperations();
				foreach (RgmsInfo item in RgmsInfo)
				{
					rastrOperations.Load(item.Name);
					num += rastrOperations.Selection("node", "sel = 1").Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * num2;
				}
			}
			return num + 1;
		}
	}

	public Shunt_KZ(object sender, ObservableCollection<RgmsInfo> rgms, List<VrnInfo> vrns, FileInfo rems, List<ShuntKZ> ShuntKZInf, bool sel, bool type, bool one, bool two)
	{
		if (rgms.Count == 0 || (ShuntKZInf.Count() == 0 && !sel) || !(one || two))
		{
			throw new InitialDataException("Не заданы все исходные данные для определения шунтов КЗ!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}" + ((ShuntKZInf.Count() == 0 && !sel) ? (Environment.NewLine + "Отсутствуют узлы в файле задания или отключен чекбокс Использовать отмеченные узлы!") : "") + ((!(one || two)) ? (Environment.NewLine + "Отключены чекбосы расчетов однофазного и двухфазного КЗ!") : ""));
		}
		RgmsInfo = rgms;
		VrnInf = vrns;
		Rems = rems;
		this.ShuntKZInf = ShuntKZInf;
		UseSelNodes = sel;
		UseTypeValU = type;
		CalcOnePhase = one;
		CalcTwoPhase = two;
		_w = sender as BackgroundWorker;
		Directory.CreateDirectory(tmp_root);
	}

	public List<ShuntResults> Calc()
	{
		int num = 0;
		List<ShuntResults> list = new List<ShuntResults>();
		foreach (RgmsInfo item in RgmsInfo)
		{
			List<Shems> list2 = new List<Shems>();
			foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
			{
				List<ShuntKZ> list3 = new List<ShuntKZ>();
				RastrOperations rastrOperations = new RastrOperations();
				rastrOperations.Load(item.Name);
				bool flag = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
				if (flag)
				{
					if (!UseSelNodes)
					{
						foreach (ShuntKZ item3 in ShuntKZInf)
						{
							ShuntKZResult shuntKZResult = default(ShuntKZResult);
							ShuntKZ shuntKZ = new ShuntKZ();
							shuntKZ.Node = item3.Node;
							rastrOperations.rgm();
							double num2 = rastrOperations.getVal("node", "vras", $"ny={item3.Node}");
							if (item3.x1 != -1.0 && (item3.u1 != -1.0 || UseTypeValU) && CalcOnePhase)
							{
								shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u1 != -1.0) ? item3.u1 : (num2 * 0.66), item3.x1, item3.r1);
								shuntKZ.r1 = shuntKZResult.r;
								shuntKZ.x1 = shuntKZResult.x;
								shuntKZ.u1 = shuntKZResult.u;
							}
							else if (item3.x1 == -1.0 && (item3.u1 != -1.0 || UseTypeValU) && CalcOnePhase)
							{
								shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u1 != -1.0) ? item3.u1 : (num2 * 0.66), Math.Sin(BaseAngle), Math.Cos(BaseAngle));
								shuntKZ.r1 = shuntKZResult.r;
								shuntKZ.x1 = shuntKZResult.x;
								shuntKZ.u1 = shuntKZResult.u;
							}
							if (CalcOnePhase)
							{
								num++;
								_w.ReportProgress(num);
							}
							if (item3.x2 != -1.0 && (item3.u2 != -1.0 || UseTypeValU) && CalcTwoPhase)
							{
								shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u2 != -1.0) ? item3.u2 : (num2 * 0.33), item3.x2, item3.r2);
								shuntKZ.r2 = shuntKZResult.r;
								shuntKZ.x2 = shuntKZResult.x;
								shuntKZ.u2 = shuntKZResult.u;
							}
							else if (item3.x2 == -1.0 && (item3.u2 != -1.0 || UseTypeValU) && CalcTwoPhase)
							{
								shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u2 != -1.0) ? item3.u2 : (num2 * 0.33), Math.Sin(BaseAngle), Math.Cos(BaseAngle));
								shuntKZ.r2 = shuntKZResult.r;
								shuntKZ.x2 = shuntKZResult.x;
								shuntKZ.u2 = shuntKZResult.u;
							}
							if (CalcTwoPhase)
							{
								num++;
								_w.ReportProgress(num);
							}
							list3.Add(shuntKZ);
						}
					}
					else
					{
						foreach (int item4 in rastrOperations.Selection("node", "sel = 1"))
						{
							ShuntKZResult shuntKZResult2 = default(ShuntKZResult);
							ShuntKZ shuntKZ2 = new ShuntKZ();
							rastrOperations.rgm();
							double num3 = rastrOperations.getVal("node", "vras", item4);
							int node = (shuntKZ2.Node = rastrOperations.getVal("node", "ny", item4));
							shuntKZResult2 = rastrOperations.FindShuntKZ(node, num3 * 0.66, Math.Sin(BaseAngle), Math.Cos(BaseAngle));
							shuntKZ2.r1 = shuntKZResult2.r;
							shuntKZ2.x1 = shuntKZResult2.x;
							shuntKZ2.u1 = shuntKZResult2.u;
							if (CalcOnePhase)
							{
								num++;
								_w.ReportProgress(num);
							}
							shuntKZResult2 = rastrOperations.FindShuntKZ(node, num3 * 0.33, Math.Sin(BaseAngle), Math.Cos(BaseAngle));
							shuntKZ2.r2 = shuntKZResult2.r;
							shuntKZ2.x2 = shuntKZResult2.x;
							shuntKZ2.u2 = shuntKZResult2.u;
							if (CalcTwoPhase)
							{
								num++;
								_w.ReportProgress(num);
							}
							list3.Add(shuntKZ2);
						}
					}
				}
				list2.Add(new Shems
				{
					ShemeName = item2.Name,
					IsStable = flag,
					Nodes = list3
				});
			}
			list.Add(new ShuntResults
			{
				RgName = item.name,
				Shems = list2
			});
		}
		return list;
	}
}
