#!/usr/bin/env wolframscript
(* ::Package:: *)

(* ::Subsection:: *)
(*Constants*)


Needs["ErrorBarPlots`"];
\[Mu]B = 9.27400968 10^-24;
\[HBar] = 1.054571726 10^-34;
e = 1.60217657 10^-19;
\[Epsilon]0 = 8.85418782 10^-12;
m = 2.838464 10^-25;
dzB=23.6;


(* ::Subsection:: *)
(*Import Data*)


ClearAll["Global`*"]
Filepath= "C:\\Users\\Christophe\\Documents\\Jarvis\\data\\";
configpath="C:\\Users\\Christophe\\Documents\\Jarvis\\config\\parameter_config.ini";



date = $ScriptCommandLine[[2]];
nexp = $ScriptCommandLine[[3]];


(*config=Import[configpath];
t1 = 1;
(*errM=ToExpression[ToExpression[config["state_detection"]["errM1"]]];
*)
*)

errM = {{0.984, 0.176}, {0.013, 0.822}};
{{PD0, PD1},{PB0, PB1}} = errM;

t1 = 2;
data = Import[Filepath<>date<>"\\"<>"test_"<>nexp<>".csv", "Data"];
description = data[[2]][[1]];

jsonparams = ImportString[StringReplace[data[[2]][[2]],{";"-> ",", "'"-> "\""}], "JSON"];
dummy = data[[2]][[3]];
counts = data[[4;;All]];

det = "det"/.jsonparams;
det = -15;
step = "step"/.jsonparams;
step = 1;
state = "state"/.jsonparams;
freq = "freq"/.jsonparams;
time = "pitime"/.jsonparams;
amp = "amp"/.jsonparams;
nruns = "runs"/.jsonparams;

{dataH, dataW} = Dimensions[counts];
nsteps = dataH/nruns; (* Get real amount of steps completed *)



(* ::Subsection:: *)
(*Init Data*)


countsA = ArrayReshape[counts[[All,1]], {nsteps, nruns}];
countsB = ArrayReshape[counts[[All,2]], {nsteps, nruns}];
countsC = ArrayReshape[counts[[All,3]], {nsteps, nruns}];

startfreq = (freq + det) 2 \[Pi] 10^3;
step = step 2 \[Pi] 10^3;
\[CapitalOmega]0approx = (2 \[Pi])/(2 time 10^-6);

noionbright = Mean[Transpose[countsC/.{c_/;c>t1 -> 0, h_/;h <= t1 -> 1}]];
oneionbright = Mean[Transpose[countsC/.{c_/;c<= t1 -> 0, h_/;h > t1 -> 1}]];
computedposition=Ordering[oneionbright,-1];
approxfreq=computedposition[[1]];
freqapprox = startfreq+approxfreq*step;
k = Map[Total,countsC/.{c_/;c<= t1 -> 0, h_/;h > t1 -> 1}];


(* ::Subsection:: *)
(*Find Probabilities *)


(* ::Text:: *)
(*MAXIMUM LIKELIHOOD METHOD: *)
(**)
(*Read Adam's chapter for a detailed explanation. *)
(**)
(*The function findProbBright returns the probability of an ion being bright, as well as sigma - and sigma +, the error bars.*)
(*Note that the errors are asymmetric around the probability, a cool unique feature of the ML method. *)


q1[p1_] := PB1 p1 + PB0 (1 - p1);
ml[p1_, k_, n_] := Log[q1[p1]^k (1 - q1[p1])^(n-k)];

findProbBright[nBright_] := Module[{maxpoint, probBright, sigmaplus, sigmaminus, sigmas},
	maxpoint = FindMaximum[{ml[p1, nBright, nruns], 0 <= p1 <= 1}, {p1, 0.5}];
	probBright = p1/. maxpoint[[2]];
	maxpoint = maxpoint[[1]];
	sigmas = sigma/.Solve[{ml[probBright, nBright, nruns] - ml[sigma, nBright, nruns] == 1/2, 0 <= sigma <= 1}, {sigma}];
	sigmas = Sort[sigmas];
	{sigmaminus, sigmaplus} = Which[Length[sigmas] == 2, sigmas, Length[sigmas] == 1, Sort[{sigmas[[1]], probBright}], 
									True, {probBright, probBright}];
	sigmaminus = probBright - sigmaminus;
	sigmaplus = sigmaplus - probBright; 
	{probBright, sigmaminus, sigmaplus}
]


ml[.8, 9, 50]//N


(*probData = Table[{startfreq + (i-1) step}, {i, 1, Length[k]}]*)


proberrData = Quiet[(findProbBright[#])&/@k];
probData = Transpose[proberrData][[1]];
freqData = Table[(i-1) step + startfreq, {i, 1, Length[probData]}];
xerr = Transpose[{Transpose[proberrData][[2]], Transpose[proberrData][[3]]}];
yerr = Table[{0,0}, Length[xerr]];
probfreqData = Transpose[{freqData, probData}];


Pupres[ \[CapitalOmega]0_,\[Omega]_,\[Omega]0_] :=\[CapitalOmega]0^2/(\[CapitalOmega]0^2+(\[Omega]-\[Omega]0)^2) Sin[(Sqrt[\[CapitalOmega]0^2+(\[Omega]-\[Omega]0)^2]\[Pi])/(2 \[CapitalOmega]0)]^2;
rabifit=NonlinearModelFit[probfreqData,Pupres[\[CapitalOmega]0,\[Omega],\[Omega]0],{{\[CapitalOmega]0,\[CapitalOmega]0approx},{\[Omega]0,freqapprox}},\[Omega]];
rabifit["BestFitParameters"]
\[Omega]0fit  = \[Omega]0/.rabifit["BestFitParameters"];
\[CapitalOmega]0fit = \[CapitalOmega]0/.rabifit["BestFitParameters"];
\[Omega]0error=rabifit["ParameterErrors"][[2]];
Success=rabifit["RSquared"]>0.985 && nsteps >40 && Max[oneionbright]>0.9;
Print[rabifit["RSquared"]>0.985 && nsteps >40 && Max[oneionbright]>0.9];
Print[\[Omega]0fit/(2 \[Pi] 10^3)];
Print[\[Omega]0error/(2 \[Pi] 10^3)];
Print[rabifit["RSquared"]];


(* ::Subsection:: *)
(*Find Error Bars*)


errorPlot[plot_, data_, xer_, yer_] := With[{
       tr = Transpose@data,
       arrow = Graphics[{Black, Line[{{0, 1/2}, {0, -1/2}}]}]},
      Module[{PlusMinus, limits, limitsRescaled, dataRescaled, lines, scale},

       scale = plot /. {ListPlot -> {# &, # &}, ListLogPlot -> {# &, Log}, 
                        ListLogLogPlot -> {Log, Log}, ListLogLinearPlot -> {Log, # &}};

       PlusMinus[a_, b_] := {a - b[[1]], a + b[[2]]};
       limits =  MapThread[MapThread[PlusMinus, {#, #2}] &,
                           {tr, {xer, yer}}];

       limitsRescaled = MapThread[Compose, {scale, limits}];   
       dataRescaled = MapThread[Compose, {scale, tr}];

       lines = Flatten[
                MapAt[Reverse, 
                      MapThread[{{#2[[1]], #}, {#2[[2]], #}} &, 
                                {Reverse@dataRescaled, limitsRescaled}, 2], 
                      {2, ;; , ;;}], 1];   

        Show[
         plot[data, PlotStyle -> {AbsolutePointSize@7, Black}, Axes -> False, Frame -> True, 
                    BaseStyle -> 18, ImageSize -> 500],
         Graphics[{Arrowheads[{{-.02, 0, arrow}, {.02, 1, arrow}}], Thick, Arrow[lines]}]
         ,
         PlotRange -> ({Min[#], Max[#]} & /@ Transpose@Flatten[lines, 1])]]]


(* ::Subsection:: *)
(*Generate Image*)


ImageToSave = If[rabifit["RSquared"] >= 0.5, 
				Show[Plot[{Pupres[\[CapitalOmega]0fit,\[Omega]*(2 \[Pi] 10^3),\[Omega]0fit]},{\[Omega],startfreq/(2 \[Pi] 10^3),(step nsteps+startfreq)/(2 \[Pi] 10^3) },PlotRange->{All,{-0.05,1.05}},PlotStyle->Directive[Thickness[0.006]],
				ImageSize->{600,380},Frame->True,AspectRatio -> 0.5,FrameStyle->Directive[Black,Thickness[0.002]],FrameLabel->{"Frequency (kHz)","\!\(\*SubscriptBox[\(P\), \(F = 1\)]\)"},
				LabelStyle->Directive[FontSize->20,FontFamily->"Helvetica",Black],PlotLabel->ToString["f0= "<>ToString[NumberForm[\[Omega]0fit/(2\[Pi] 10^3),9] ]<>" "<>ToString[PlusMinus[NumberForm[\[Omega]0error/(2 \[Pi] 10^3),1]]]<>" kHz, t\[Pi]="<>ToString[(2 \[Pi] 10^6)/( 2 \[CapitalOmega]0fit)]<>" \[Mu]s"//DisplayForm]],
                errorPlot[ListPlot, {#[[1]]/(2 \[Pi] 10^3), #[[2]]}&/@probfreqData, yerr, xerr], ImageSize->{600,400}], 
				Show[errorPlot[ListPlot, {#[[1]]/(2 \[Pi] 10^3), #[[2]]}&/@probfreqData, yerr, xerr],
				ImageSize->{600,380},Frame->True,AspectRatio -> 0.5,FrameStyle->Directive[Black,Thickness[0.002]],FrameLabel->{"Frequency (kHz)","\!\(\*SubscriptBox[\(P\), \(F = 1\)]\)"},
				LabelStyle->Directive[FontSize->20,FontFamily->"Helvetica",Black],
                 ImageSize->{600,400}]];


Export[Filepath<>date<>"\\image_"<>ToString[nexp]<>".png",ImageToSave];
