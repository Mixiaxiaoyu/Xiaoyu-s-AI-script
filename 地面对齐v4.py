#对面对齐插件由B站米夏小雨编写




import c4d


def main():
    # 获取选中的对象列表
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    if not selected_objects:
        # 当没有选中对象时弹出提示
        c4d.gui.MessageDialog("请选中对象后再使用", c4d.GEMB_OK)
        return

    for obj in selected_objects:
        try:
            # 将对象转换为可编辑对象
            if obj.GetType() == c4d.Ospline:
                editable_obj = obj.GetRealSpline()
            elif obj.GetType() == c4d.Opolygon:
                # 对于多边形对象，使用 SendModelingCommand 进行转换
                res = c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[obj], mode=c4d.MODELINGCOMMANDMODE_ALL, bc=c4d.BaseContainer(), doc=doc)
                if res:
                    editable_obj = res[0]
                else:
                    print("Failed to convert object to editable.")
                    print(f"SendModelingCommand result: {res}")
                    continue
                # 确保 editable_obj 有 GetAllPoints 方法，否则继续下一个对象
                if not hasattr(editable_obj, 'GetAllPoints'):
                    c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                    continue
                # 获取对象的点
                points = editable_obj.GetAllPoints()
            elif obj.GetType() == 5140:  # 处理对象类型 5140
                # 直接处理 5140 类型对象的 Y 轴归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                obj.SetMg(offset_matrix * obj.GetMg())
                continue
            elif obj.GetType() == 5100:  # 处理对象类型 5100
                # 先判断是否有点
                if not hasattr(obj, 'GetAllPoints'):
                    c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                    continue
                points = obj.GetAllPoints()
            elif obj.GetType() == 5166:  # 处理对象类型 5166
                # 直接处理 5166 类型对象的 Y 轴归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                obj.SetMg(offset_matrix * obj.GetMg())
                continue
            elif isinstance(obj, c4d.BaseObject):  # 处理一般对象类型
                # 尝试使用 SendModelingCommand 进行转换
                res = c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[obj], mode=c4d.MODELINGCOMMANDMODE_ALL, bc=c4d.BaseContainer(), doc=doc)
                if res:
                    editable_obj = res[0]
                else:
                    print("Failed to convert c4d.BaseObject to editable.")
                    continue
                # 确保 editable_obj 有 GetAllPoints 方法，否则继续下一个对象
                if not hasattr(editable_obj, 'GetAllPoints'):
                    c4d.gui.MessageDialog("无法支持此操作，请尝试将对象转换成多边形对象再进行操作", c4d.GEMB_OK)
                    continue
                # 获取对象的点
                points = editable_obj.GetAllPoints()
            else:
                continue

            # 处理对象点数量为 0 的情况
            if 'points' not in locals():
                # 直接按全局坐标 Y 归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                obj.SetMg(offset_matrix * obj.GetMg())
                continue

            # 对于有多个点的对象进行以下处理
            if len(points) == 0:
                # 直接按全局坐标 Y 归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
                obj.SetMg(offset_matrix * obj.GetMg())
                continue
            elif len(points) == 1:
                # 只有一个点的情况，直接以世界坐标轴来计算 Y 轴归零
                offset = c4d.Vector(0, -obj.GetMg().off.y, 0)
                offset_matrix = c4d.Matrix()
                offset_matrix.off = offset
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
                # 移动对象
                obj.SetMg(offset_matrix * obj.GetMg())
        except Exception as e:
            print(f"Error occurred: {e}")

    c4d.EventAdd()


if __name__ == "__main__":
    
    
    
    
    
    
    
    
    main()