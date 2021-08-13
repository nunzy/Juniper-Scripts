import yaml
from jinja2 import Template

### Render the jinja2 template
mytemplate = Template(open('template/CustVRF.j2').read())
mydata = yaml.load(open('config/CustSetup.yml').read(), Loader=yaml.BaseLoader)
myconfig = mytemplate.render(mydata)
print("\n### Here's the full config:")
print(myconfig)
