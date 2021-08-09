#!/usr/bin/env wolframscript
(* ::Package:: *)

(*Print[$ScriptCommandLine[[2]]]*)
Filepath = Directory[]<>"\\Jarvis\\data\\";
configpath = Directory[]<>"\\Jarvis\\config\\parameter_config.ini";
configpath = "C:\\Users\\Christophe\\Documents\\Jarvis\\config\\parameter_config.ini";
date = "190404";
data = Import[configpath, "Data"]
Print[data]






