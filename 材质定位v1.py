#对面对齐插件由B站米夏小雨编写

import c4d
import c4d.gui


def main():
    try:
        # 获取活动文档
        doc = c4d.documents.GetActiveDocument()
        # 获取选中的对象
        selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
        if not selected_objects:
            c4d.gui.MessageDialog("没有选中对象，请选择对象。")
            return

        # 存储选中对象的材质
        materials = []
        for obj in selected_objects:
            # 获取对象的材质标签
            tags = obj.GetTags()
            for tag in tags:
                if isinstance(tag, c4d.TextureTag):
                    # 获取纹理标签的材质
                    mat = tag[c4d.TEXTURETAG_MATERIAL]
                    if mat:
                        materials.append(mat)

        # 确保材质列表不为空
        if not materials:
            print("未找到任何材质。")
            return

        # 获取第一个材质
        first_material = doc.GetFirstMaterial()
        if not first_material:
            print("材质列表为空。")
            return

        # 将找到的材质移到第一个材质的最前面
        for mat in materials:
            # 先将材质从当前位置移除
            mat.Remove()
            # 将其插入到第一个材质的前面
            mat.InsertBefore(first_material)

        # 滚动到第一个材质
        c4d.CallCommand(100004768)  # 滚动材质列表，使其可见

    except Exception as e:
        print(f"发生异常: {e}")


if __name__ == "__main__":
    main()