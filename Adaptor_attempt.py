"""Adaptor to convert BLUEMIRA and PROCESS parameters to common Reactor class"""
#(Currently untested WIP)

class BasicParameters:
    """Adapting basic BLUEMIRA or PROCESS data classes to common format"""

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

    def __init__(self, data_input):
        self.data_input  = data_input
        
        if type(self.data_input) == 'process':
            self.adapt_process()
        else:
            self.adapt_bluemira()

process_data = MilesPROCESSextraction('.DAT')

adapted_params = BasicParameters(process_data)

