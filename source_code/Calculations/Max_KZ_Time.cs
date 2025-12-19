using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using rst_operations;

namespace DynStabSpace;

public class Max_KZ_Time
{
	private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Предельное время КЗ";

	private BackgroundWorker _w;

	private ObservableCollection<RgmsInfo> RgmsInfo;

	private ObservableCollection<ScnsInfo> ScnsInfo;

	private List<VrnInfo> VrnInf;

	private FileInfo Rems;

	private double CrtTimePrecision;

	private double CrtTimeMax;

	public string root => tmp_root;

	public int Max => RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() + 1;

	public Max_KZ_Time(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, double time_precision, double max_time)
	{
		if (rgms.Count() == 0 || scns.Count() == 0 || max_time == 0.0)
		{
			throw new InitialDataException("Не заданы все исходные данные для определения предельного времени отключения КЗ!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}{Environment.NewLine}" + $"Максимальное время отключения КЗ составляет - {max_time}");
		}
		RgmsInfo = rgms;
		ScnsInfo = scns;
		VrnInf = vrns;
		Rems = rems;
		CrtTimePrecision = time_precision;
		CrtTimeMax = max_time;
		_w = sender as BackgroundWorker;
		Directory.CreateDirectory(tmp_root);
	}

	public List<CrtTimeResults> Calc()
	{
		int num = 0;
		List<CrtTimeResults> list = new List<CrtTimeResults>();
		foreach (RgmsInfo item in RgmsInfo)
		{
			List<CrtShems> list2 = new List<CrtShems>();
			foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
			{
				List<CrtTimes> list3 = new List<CrtTimes>();
				CrtShems crtShems = new CrtShems();
				crtShems.ShemeName = item2.Name;
				foreach (ScnsInfo item3 in ScnsInfo)
				{
					RastrOperations rastrOperations = new RastrOperations();
					rastrOperations.Load(item.Name);
					rastrOperations.Load(item3.Name);
					crtShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
					if (crtShems.IsStable)
					{
						list3.Add(new CrtTimes
						{
							ScnName = item3.name,
							CrtTime = rastrOperations.FindCrtTime(CrtTimePrecision, CrtTimeMax)
						});
						num++;
						_w.ReportProgress(num);
					}
				}
				crtShems.Times = list3;
				list2.Add(crtShems);
			}
			list.Add(new CrtTimeResults
			{
				RgName = item.name,
				CrtShems = list2
			});
		}
		return list;
	}
}
