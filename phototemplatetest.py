from phototemplate import TemplateReader
from phototemplate import TemplateManager

print("#--------------------------------------\n TemplateReader")
templateReader = TemplateReader("./templates/TestTemplate/template.xml")
print(vars(templateReader))

print("#--------------------------------------\n TemplateManager")
templateManager = TemplateManager("./templates")
