#对面对齐插件由B站米夏小雨编写



import c4d

# 定义一个小的阈值，用于判断是否已经对齐地面
THRESHOLD = 1e-5

def get_deformed_points(obj):
    """获取对象变形后的所有点坐标（考虑曲面细分等变形器）"""
    if obj is None:
        return None

    # 获取对象的变形数据
    deformed = obj.GetDeformCache()
    if deformed is None:
        deformed = obj.GetCache()  # 如果没有变形缓存，尝试获取普通缓存
    if deformed is None:
        deformed = obj  # 如果没有缓存，直接使用对象本身

    # 获取变形后的点坐标
    try:
        points = deformed.GetAllPoints()
        return points
    except AttributeError:
        return None

def is_object_aligned_to_ground(obj):
    """检查对象是否已经对齐地面"""
    points = get_deformed_points(obj)
    if points is None or len(points) == 0:
        return abs(obj.GetMg().off.y) < THRESHOLD

    min_y = float('inf')
    for point in points:
        world_point = obj.GetMg() * point
        if world_point.y < min_y:
            min_y = world_point.y

    return abs(min_y) < THRESHOLD

def main():
    # 获取选中的对象列表
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    if not selected_objects:
        # 当没有选中对象时弹出提示
        c4d.gui.MessageDialog("请选中对象后再使用", c4d.GEMB_OK)
        return

    all_aligned = True
    for obj in selected_objects:
        if not is_object_aligned_to_ground(obj):
            all_aligned = False
            break

    if all_aligned:
        c4d.gui.MessageDialog("对象已对齐地面", c4d.GEMB_OK)
        return

    # 记录撤销点
    doc.StartUndo()

    for obj in selected_objects:
        try:
            # 尝试获取变形后的点
            points = get_deformed_points(obj)

            # 如果获取点失败或者点数量为 0，采用原本代码逻辑处理
            if points is None or len(points) == 0:
                if obj.GetType() == c4d.Ospline:
                    editable_obj = obj.GetRealSpline()
                    if hasattr(editable_obj, 'GetAllPoints'):
                        points = editable_obj.GetAllPoints()
                    else:
                        c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                        continue
                elif obj.GetType() == c4d.Opolygon:
                    # 对于多边形对象，使用 SendModelingCommand 进行转换
                    res = c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[obj],
                                                        mode=c4d.MODELINGCOMMANDMODE_ALL, bc=c4d.BaseContainer(),
                                                        doc=doc)
                    if res:
                        editable_obj = res[0]
                        if hasattr(editable_obj, 'GetAllPoints'):
                            points = editable_obj.GetAllPoints()
                        else:
                            c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                            continue
                    else:
                        print("Failed to convert object to editable.")
                        print(f"SendModelingCommand result: {res}")
                        continue
                elif obj.GetType() == 5140:  # 处理对象类型 5140
                    # 直接处理 5140 类型对象的 Y 轴归零
                    offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                    offset_matrix = c4d.Matrix()
                    offset_matrix.off = offset
                    # 记录撤销操作
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                    obj.SetMg(offset_matrix * obj.GetMg())
                    continue
                elif obj.GetType() == 5100:  # 处理对象类型 5100
                    # 先判断是否有点
                    if hasattr(obj, 'GetAllPoints'):
                        points = obj.GetAllPoints()
                    else:
                        c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                        continue
                elif obj.GetType() == 5166:  # 处理对象类型 5166
                    # 直接处理 5166 类型对象的 Y 轴归零
                    offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                    offset_matrix = c4d.Matrix()
                    offset_matrix.off = offset
                    # 记录撤销操作
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                    obj.SetMg(offset_matrix * obj.GetMg())
                    continue
                elif isinstance(obj, c4d.BaseObject):  # 处理一般对象类型
                    # 尝试使用 SendModelingCommand 进行转换
                    res = c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[obj],
                                                        mode=c4d.MODELINGCOMMANDMODE_ALL, bc=c4d.BaseContainer(),
                                                        doc=doc)
                    if res:
                        editable_obj = res[0]
                        if hasattr(editable_obj, 'GetAllPoints'):
                            points = editable_obj.GetAllPoints()
                        else:
                            c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                            continue
                    else:
                        print("Failed to convert c4d.BaseObject to editable.")
                        continue
                else:
                    continue

            # 处理对象点数量为 0 的情况
            if 'points' not in locals() or len(points) == 0:
                # 直接按全局坐标 Y 归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                # 记录撤销操作
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                obj.SetMg(offset_matrix * obj.GetMg())
                continue

            # 对于有多个点的对象进行以下处理
            if len(points) == 1:
                # 只有一个点的情况，直接以世界坐标轴来计算 Y 轴归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                # 记录撤销操作
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                obj.SetMg(offset_matrix * obj.GetMg())
                continue
            else:
                # 选择对齐方式，这里以最小 Y 坐标点为例
                # 初始化最小 Y 坐标和最小 Y 坐标点
                min_y = float('inf')
                min_y_point = None
                for point in points:
                    world_point = obj.GetMg() * point
                    if world_point.y < min_y:
                        min_y = world_point.y
                        min_y_point = world_point

                if min_y_point is None:
                    print("No valid min Y point found.")
                    continue

                # 计算 Y 轴偏移量
                offset = c4d.Vector(0, -min_y, 0)

                # 计算全局坐标偏移矩阵
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                # 记录撤销操作
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                # 移动对象
                obj.SetMg(offset_matrix * obj.GetMg())
        except Exception as e:
            print(f"Error occurred: {e}")

    # 完成撤销操作记录
    doc.EndUndo()

    c4d.EventAdd()

if __name__ == "__main__":
    main()