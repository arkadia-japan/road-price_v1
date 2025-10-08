"""
不動産物件情報を格納するデータクラス
"""
from dataclasses import dataclass


@dataclass
class PropertyData:
    """不動産物件情報を格納するデータクラス"""

    address: str  # 所在地
    land_area: float  # 土地面積（㎡）
    building_structure: str  # 建物の構造
    total_floor_area: float  # 延床面積（㎡）
    build_year: int  # 建築年

    def __str__(self) -> str:
        """物件情報を読みやすい形式で出力"""
        return (
            f"物件情報:\n"
            f"  所在地: {self.address}\n"
            f"  土地面積: {self.land_area}㎡\n"
            f"  建物構造: {self.building_structure}\n"
            f"  延床面積: {self.total_floor_area}㎡\n"
            f"  建築年: {self.build_year}年"
        )
