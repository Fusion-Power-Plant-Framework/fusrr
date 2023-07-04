"""Adaptor to convert BLUEMIRA and PROCESS parameters to common Reactor class"""
#(Currently untested WIP)

class BasicParameters:
    """Adapting basic BLUEMIRA or PROCESS data classes to common format"""
    def __init__(self, data_input):
        self.data_input  = data_input
        
        if self.data_input == MFile: ###file type/ way to define PROCESS vs BLUEMIRA (path('my_file').suffix = DAT?)
            self.adapt_process()
        else:
            self.adapt_bluemira()
    
    def adapt_process(self):
        """Convert parameters from PROCESS dataclasses to generic format"""
        from Dictionary_Basic import process_param
        for param_name, param_value in self.data_input.items():
            generic_name = process_param[param_name]
            setattr(self, generic_name, param_value)

    def adapt_bluemira(self):
        """Convert parameters from BLUEMIRA dataclesses to generic format"""
        from Dictionary_Basic import bluemira_param
        for param_name, param_value in self.data_input.items():
            generic_name = bluemira_param[param_name]
            setattr(self, generic_name, param_value)

input_data = OutputParams.from_file('baseline_MFILE.DAT')

adapted_params = BasicParameters(input_data)

