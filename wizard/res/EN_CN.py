CN_property = {
    'Attribute': '属性',
    'Default': '默认',
    'Opacity': '不透明度',
    'Text': '文本',
    'VarName': '变量名',
    'Event': '动作',
    'Instance': '组件',
    'width': '宽',
    'height': '高',
    'left': '左',
    'top': '上',
    'max': '最大值',
    'value': '当前值',
    'background-color': '颜色',
    'font-size': '字号',
    'color': '字色',
    'Enter Text:': '输入文字：',
    'check_connection': '检查串口链接',
    'speed': '速度'
}

CN_widget = {
    'Basic': '基础',
    'Service': '服务',
    'Instance': '案例',
    'Button': '按钮',
    'Label': '文字',
    'DropDown': '下拉框',
    'Image': '图片',
    'CheckBox': '选择框',
    'SpinBox': '数值',
    'Slider': '滑块',
    'ColorPicker': '调色盘',
    'Date': '日期',
    'Link': '链接',
    'CheckBoxLabel': '文本选择框',
    'ListView': '列表框',
    'Progress': '进度条',
    'FileUploader': '文件传输',
    'TextInput': '输入框',
    'Camera': '摄像头',
    'stage': '基础容器',
    'aid_bot': ''
}

CN_service = {
    'hair_segmentation': '头发识别',
    'face_detection': '面部识别',
    'hand_tracking': '手部识别',
    'pose_detection': '姿势识别',
    'objectron': '结构识别',
    'chip_detection': '工业检测',
    'aid_bot': '机器人'
}

CN_dialog = {
    'open_project': '打开项目',
    'open_project_des': '选择一个由本软件生成的python文件打开',
    'cancel': '取消',
    'ok': '确认',
    'save_project': '保存项目',
    'save_project_des': '确认文件名和保存路径',
    'save_project_name': '文件名称',
    'filename_input': '输入文件名...',
    'open_error': '项目错误',
    'open_error_des': '由于发生以下错误，无法打开项目'
}


def varname_CN(varname):
    components = varname.split('_')
    prefix = CN_widget.get(components[0], None)
    if prefix is None:
        return CN_service[varname]
    if len(components) == 1:
        return CN_widget[components[0]]
    return CN_widget[components[0]] + ' ' + components[1]
