using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using rst_operations;

namespace DynStabSpace;

public class MdpStabilityCalc
{
	private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} МДП ДУ";

	private BackgroundWorker _w;

	private ObservableCollection<RgmsInfo> RgmsInfo;

	private ObservableCollection<ScnsInfo> ScnsInfo;

	private List<VrnInfo> VrnInf;

	private FileInfo Rems;

	private FileInfo VIR;

	private FileInfo Sechen;

	private FileInfo LAPNU;

	private List<SchInfo> SchInf;

	private List<KprInfo> KprInf;

	private string lpns;

	private int SelectedSch;

	private bool DynNoPA;

	private bool DynWithPA;

	public bool UseLPN;

	public string root => tmp_root;

	public int Max
	{
		get
		{
			int num = (DynNoPA ? 1 : 0) + (DynWithPA ? 1 : 0);
			return RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() * num + 1;
		}
	}

	public MdpStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, FileInfo vir, FileInfo sechen, FileInfo lapnu, List<SchInfo> schs, List<KprInfo> kprs, string lpns = "", int selected_sch = 0, bool no_pa = true, bool with_pa = false, bool lpn = false)
	{
		if (rgms.Count() == 0 || scns.Count() == 0 || vir.Name == null || sechen.Name == null || (lapnu.Name == null && with_pa) || (lpn && sechen.Name == null))
		{
			throw new InitialDataException("Не заданы все исходные данные для определения допустимых перетоков мощности по критерию обеспечения динамической устойчивости генерирующего оборудования!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}" + ((vir.Name == null) ? (Environment.NewLine + "Отсутствует траектория утяжеления!") : "") + ((sechen.Name == null) ? (Environment.NewLine + "Отсутствует файл контролируемых сечений!") : "") + ((lapnu.Name == null && with_pa) ? (Environment.NewLine + "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!") : "") + ((lpn && sechen.Name == null) ? (Environment.NewLine + "Используется файл ПА в формате lpn, но не загружен файл сечений!") : ""));
		}
		RgmsInfo = rgms;
		ScnsInfo = scns;
		VrnInf = vrns;
		Rems = rems;
		VIR = vir;
		Sechen = sechen;
		LAPNU = lapnu;
		SchInf = schs;
		KprInf = kprs;
		this.lpns = lpns;
		SelectedSch = selected_sch;
		DynNoPA = no_pa;
		DynWithPA = with_pa;
		UseLPN = lpn;
		_w = sender as BackgroundWorker;
		Directory.CreateDirectory(tmp_root);
	}

	public List<MdpResults> Calc()
	{
		int num = 0;
		List<MdpResults> list = new List<MdpResults>();
		string text = tmp_root + "\\\\mdp_calc_tmp.rst";
		foreach (RgmsInfo item in RgmsInfo)
		{
			List<MdpShems> list2 = new List<MdpShems>();
			foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
			{
				MdpShems mdpShems = new MdpShems();
				List<MdpEvents> list3 = new List<MdpEvents>();
				mdpShems.ShemeName = item2.Name;
				foreach (ScnsInfo item3 in ScnsInfo)
				{
					RastrOperations rastrOperations = new RastrOperations();
					if (!mdpShems.IsReady)
					{
						rastrOperations.Load(item.Name);
						rastrOperations.DynSettings();
						mdpShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
						rastrOperations.Save(text);
						mdpShems.IsReady = true;
						if (mdpShems.IsStable)
						{
							rastrOperations.Load(Sechen.Name);
							rastrOperations.Load(VIR.Name);
							mdpShems.Pstart = rastrOperations.getVal("sechen", "psech", SelectedSch);
							mdpShems.MaxStep = rastrOperations.Run_Ut();
							mdpShems.Ppred = rastrOperations.getVal("sechen", "psech", SelectedSch);
							rastrOperations.Load(text);
							rastrOperations.Load(VIR.Name);
							mdpShems.MaxStep = rastrOperations.Step(mdpShems.MaxStep * 0.9);
							double num2 = rastrOperations.getVal("sechen", "psech", SelectedSch);
							while (Math.Abs(num2 - mdpShems.Ppred * 0.9) > 2.0)
							{
								rastrOperations.Load(text);
								rastrOperations.Load(VIR.Name);
								mdpShems.MaxStep = rastrOperations.Step(mdpShems.MaxStep * mdpShems.Ppred * 0.9 / num2);
								num2 = rastrOperations.getVal("sechen", "psech", SelectedSch);
							}
							rastrOperations.Save(text);
						}
					}
					if (!mdpShems.IsStable)
					{
						break;
					}
					List<Values> list4 = new List<Values>();
					List<Values> list5 = new List<Values>();
					List<Values> list6 = new List<Values>();
					List<Values> list7 = new List<Values>();
					double noPaMdp = -1.0;
					double withPaMdp = -1.0;
					double num3 = Math.Max(2.0, Math.Min(10.0, Math.Floor(mdpShems.Ppred * 0.02)));
					if (DynNoPA)
					{
						rastrOperations.Load(text);
						rastrOperations.Load(Sechen.Name);
						rastrOperations.Load(VIR.Name);
						rastrOperations.Load(item3.Name);
						rastrOperations.LoadTemplate(".dfw");
						DynamicResult dynamicResult = rastrOperations.RunDynamic(_ems: true);
						if (dynamicResult.IsSuccess && !dynamicResult.IsStable)
						{
							double num4 = rastrOperations.getVal("sechen", "psech", SelectedSch);
							double num5 = mdpShems.Pstart;
							double num6 = 0.0;
							double num7 = 0.0 - mdpShems.MaxStep;
							double step = num6 + (num7 - num6) * 0.5;
							while (dynamicResult.IsSuccess && (Math.Abs(num4 - num5) > num3 || !dynamicResult.IsStable))
							{
								rastrOperations.Load(text);
								rastrOperations.Load(VIR.Name);
								double num8 = rastrOperations.Step(step);
								dynamicResult = rastrOperations.RunDynamic(_ems: true);
								if (dynamicResult.IsSuccess && dynamicResult.IsStable)
								{
									num7 = num8;
									num5 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								}
								else
								{
									num6 = num8;
									num4 = rastrOperations.getVal("sechen", "psech", SelectedSch);
									if (num6 <= num7 || Math.Floor(num4) <= Math.Floor(num5) + 2.0)
									{
										num7 -= 2.0;
									}
								}
								step = num6 + (num7 - num6) * 0.5;
							}
							noPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
						}
						else if (dynamicResult.IsSuccess && dynamicResult.IsStable)
						{
							noPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
						}
						foreach (SchInfo item4 in SchInf.Where((SchInfo k) => k.Control))
						{
							list4.Add(new Values
							{
								Id = item4.Id,
								Name = item4.Name,
								Value = rastrOperations.getVal("sechen", "psech", item4.Id)
							});
						}
						foreach (KprInfo item5 in KprInf)
						{
							list5.Add(new Values
							{
								Id = item5.Id,
								Name = item5.Name,
								Value = rastrOperations.getVal(item5.Table, item5.Col, item5.Selection)
							});
						}
						num++;
						_w.ReportProgress(num);
					}
					if (DynWithPA)
					{
						rastrOperations.Load(text);
						rastrOperations.Load(Sechen.Name);
						rastrOperations.Load(VIR.Name);
						if (UseLPN)
						{
							rastrOperations.Load(Sechen.Name);
							rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
						}
						else
						{
							rastrOperations.Load(item3.Name);
							rastrOperations.Load(LAPNU.Name);
						}
						DynamicResult dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
						if (dynamicResult2.IsSuccess && !dynamicResult2.IsStable)
						{
							double num9 = rastrOperations.getVal("sechen", "psech", SelectedSch);
							double num10 = mdpShems.Pstart;
							double num11 = 0.0;
							double num12 = 0.0 - mdpShems.MaxStep;
							double step2 = num11 + (num12 - num11) * 0.5;
							while (dynamicResult2.IsSuccess && (Math.Abs(num9 - num10) > num3 || !dynamicResult2.IsStable))
							{
								rastrOperations.Load(text);
								rastrOperations.Load(VIR.Name);
								double num13 = rastrOperations.Step(step2);
								if (UseLPN)
								{
									rastrOperations.Load(Sechen.Name);
									rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
								}
								else
								{
									rastrOperations.Load(item3.Name);
									rastrOperations.Load(LAPNU.Name);
								}
								dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
								if (dynamicResult2.IsSuccess && dynamicResult2.IsStable)
								{
									num12 = num13;
									num10 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								}
								else
								{
									num11 = num13;
									num9 = rastrOperations.getVal("sechen", "psech", SelectedSch);
									if (num11 <= num12 || Math.Floor(num9) <= Math.Floor(num10) + 2.0)
									{
										num12 -= 2.0;
									}
								}
								step2 = num11 + (num12 - num11) * 0.5;
							}
							withPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
						}
						else if (dynamicResult2.IsSuccess && dynamicResult2.IsStable)
						{
							withPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
						}
						foreach (SchInfo item6 in SchInf.Where((SchInfo k) => k.Control))
						{
							list6.Add(new Values
							{
								Id = item6.Id,
								Name = item6.Name,
								Value = rastrOperations.getVal("sechen", "psech", item6.Id)
							});
						}
						foreach (KprInfo item7 in KprInf)
						{
							list7.Add(new Values
							{
								Id = item7.Id,
								Name = item7.Name,
								Value = rastrOperations.getVal(item7.Table, item7.Col, item7.Selection)
							});
						}
						num++;
						_w.ReportProgress(num);
					}
					list3.Add(new MdpEvents
					{
						Name = item3.name,
						NoPaSechen = list4,
						NoPaKpr = list5,
						WithPaSechen = list6,
						WithPaKpr = list7,
						NoPaMdp = noPaMdp,
						WithPaMdp = withPaMdp
					});
				}
				mdpShems.Events = list3;
				list2.Add(mdpShems);
			}
			list.Add(new MdpResults
			{
				RgName = item.name,
				MdpShems = list2
			});
		}
		File.Delete(text);
		return list;
	}
}
