
# Custom BigFix Dashboards 

This folder contains custom BigFix dashboards that can be loaded though the "Debug -> Load Wizard..." menu or added directly as a file to a custom site.

## Current contents:

- `BFLabsMaintenanceWindows.ojo` 
 
    Dashboard that allows users to specify maintenance window configuration based on date, week of month, day of week, or even offset from specific week and day of the month (i.e. 2 days after "patch Tuesday")
    
- `ScriptTaskBuilder.ojo`  

Gives user ability to wrap any custom shell, powershell or batch script in a task. It escapes all the special BigFix Action script characters appropriately. 

- `PatchChannels.ojo`  


Provides new way of doing automated patching through user defined patch channels (guide [here](https://github.com/bigfix/content/blob/master/dashboards/BigFix%20Labs%20Patch%20Channels.docx) )



