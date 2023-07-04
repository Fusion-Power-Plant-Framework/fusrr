"""Adapter to convert BLUEMIRA and PROCESS parameters to common Reactor class"""
#(Currently WIP)
from extract_params import OutputParams
from dataclasses import asdict

input_data = OutputParams.from_file('baseline_MFILE.DAT')
input = asdict(input_data)

class BasicParameters:
    """Adapting basic BLUEMIRA or PROCESS data classes to common format"""
    def __init__(self, data_input):
        self.data_input  = data_input
        
        if self.data_input == 'BLUEMIRA': 
            self.adapt_bluemira()
        else:
            self.adapt_process()
    
    def adapt_process(self):
        """Convert parameters from PROCESS dataclasses to generic format"""
        from Dictionary_Basic import process_param
        for param_name, param_value in input.items():
            generic_name = process_param[param_name]
            setattr(self, generic_name, param_value)

    def adapt_bluemira(self):
        """Convert parameters from BLUEMIRA dataclesses to generic format"""
        from Dictionary_Basic import bluemira_param
        for param_name, param_value in self.data_input.items():
            generic_name = bluemira_param[param_name]
            setattr(self, generic_name, param_value)



adapted_params = BasicParameters(input_data)

