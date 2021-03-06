import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore
import pickle
import sys, pandas as pd
from sample_data.dataset import countries
from ui.datacube_ui import Ui_riskViewer

class Node:
    def __init__(self,id, values):
        self.id = id
        self.children = []
        self.values = values
    def addchild(self,child):
        self.children.append(child)
    def __repr__(self):
        return f"<{self.id}>: {self.values}"


def populatenode(node, df, columns):
    if len(columns) == 0:
        return
    
    for group, subdf in df.groupby(columns[0]):
        #print(group)
        values_list = []
        for column, aggregation in values:
            series = subdf[column]
            if aggregation == 'sum':
                value = series.sum()
            else:
                all_values = set(series.values)
                value = list(all_values)[0] if len(all_values) == 1 else ''
            values_list.append(value)
        subnode = Node(group, values_list)
        #print(f"Adding {subnode} to {node}")
        node.addchild(subnode)
        populatenode(subnode,subdf, columns[1:])
    

def add_to_tree(qtw,node):
    for child in node.children:
        formatted_values = [str(child.id)]
        for (col,_),value in zip(values,child.values):
            formatter = formatters.get(col, lambda x: x)
            value = formatter(value)
            formatted_values.append(str(value))

        child_node = qt.QTreeWidgetItem(qtw,formatted_values)
        for i,_ in enumerate(values):
            child_node.setData(i+1,qtcore.Qt.TextAlignmentRole, qtcore.Qt.AlignRight)
        #child_node.setProperty('class','red')
        add_to_tree(child_node,child)


df = pd.DataFrame(countries)
print(df)
root = Node('root', [])


columns = ['continent', 'name', 'form', 'year' ]
values = [('form','uniq'), ('gdp','sum'), ('oil','sum')]

formatters = {
    'gdp': lambda x: f"{x:.2f}",
    'oil': lambda x: f"{x:.2f}",
}

        
app = qt.QApplication([])

windows = []

def debug():
    a = 1


settings_file = 'settings/settings.pkl'

def load_settings():
    import os
    if not os.path.exists(settings_file):
        print("No settings saved")
        return []

    with open(settings_file,'rb') as f:
        settings = pickle.loads(f.read())
    print("Loaded settings from ", settings_file)
    print(settings)
    return settings

def save_settings():
    settings = []
    for window in windows:
        settings.append(window.geometry())

    print("Saving settings to ", settings_file)
    print(settings)

    with open(settings_file,'wb') as f:
        f.write(pickle.dumps(settings))


def exit_app():
    save_settings()
    sys.exit(0)

def new_window():
    sheet = open('ui/style.css','r').read()
    app.setStyleSheet(sheet)
    window = qt.QMainWindow()
    layout = qt.QVBoxLayout(window)
    ui = Ui_riskViewer()
    ui.setupUi(window)

    ui.newWindowButton.clicked.connect(lambda: windows.append(new_window()))
    ui.debugButton.clicked.connect(debug)
    ui.saveSettingsButton.clicked.connect(save_settings)
    ui.loadSettingsButton.clicked.connect(load_settings)
    ui.exitButton.clicked.connect(exit_app)

    tw = ui.riskTree
    tw.setAlternatingRowColors(True)
    populatenode(root,df,columns)
    add_to_tree(tw,root)

    values_labels = [f'{agg}({col})' for col,agg in values]
    tw.setHeaderLabels([""] + values_labels)
    header = tw.header()
    header.setSectionResizeMode(qt.QHeaderView.ResizeToContents)
    header.setStretchLastSection(False)
    #header.setSectionResizeMode(5, qt.QHeaderView.Stretch)

    window.show()
    return window

settings = load_settings()
if not len(settings):
    windows.append(new_window())
else:
    for geometry in settings:
        window = new_window()
        #window.resize(w['size'])
        window.setGeometry(geometry)
        windows.append(window)

#windows.append(new_window())
#new_window()
sys.exit(app.exec_())