import asyncio
import logging
from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from utils.middleware import rate_limit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化mcp实例
mcp = FastMCP("nrcc-search", host='localhost', port=8000, log_level='INFO')
USER_AGENT = "Mozilla/5.0"

base_url = "https://whpdj.mem.gov.cn/internet/common/chemical"

async def search_chemicals_list(chemName: str, chemCas: str) -> Any:
    get_chem_id_url = base_url + "/queryChemicalList"
    payload = {
    "status": "1",
    "chemName": str(chemName),
    "chemCas": str(chemCas),
    "chemEnglishName": "",
    "isFuzzy": "1",
    "page": {
        "current": "1",
        "size": 5
    }
}
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": USER_AGENT
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(get_chem_id_url, json=payload, headers=headers, timeout=30.0)
            # response.raise_for_status()
            logging.info(f"NRCC Search Response: {response.json()}")
            return response.json()
        except Exception as e:
            logging.error(f"NRCC Search List Error: {e}")
            return "chemicals list is empty."

async def search_chemical_detail(chem_id: str) -> Any:
    url = base_url + "/queryChemicalById"
    payload = {
    "idenDataId": chem_id,
    "status": "1"
}
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": USER_AGENT
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            logging.info(f"NRCC Search Detail Response: {response.json()}")
            return response.json()
        except Exception as e:
            logging.error(f"NRCC Search Error: {e}")
            return "No data found."

async def format_chemicals_list(results: Any) -> str:
    if not results or 'obj' not in results or 'records' not in results['obj']:
        return "No results found."

    records = results['obj']['records']
    formatted_results = []
    for record in records:
        chemName = record.get('chemName', 'N/A')
        chemCas = record.get('chemCas', 'N/A')
        chemAlias = record.get('chemAlias', 'N/A')
        chemEnglishName = record.get('chemEnglishName', 'N/A')
        idendataid = record.get('idenDataId', 'N/A')
        formatted_results.append(
            f"化学品名称: {chemName}\n"
            f"CAS号: {chemCas}\n"
            f"化学品别名: {chemAlias}\n"
            f"化学品英文名: {chemEnglishName}\n"
            f"idenDataId: {idendataid   }\n"
            "-------------------------\n"
        )

    return "\n".join(formatted_results)

async def format_chemical_detail(result: Any) -> str:
    if not result or 'obj' not in result:
        return "No chemical details found."

    obj = result['obj']
    # Convert Array to string
    def array_to_string(arr):
        if isinstance(arr, list):
            return ", ".join(str(item) for item in arr)
        return str(arr)
    param_features = obj.get('parameterFeaturesArr', [])
    pictogramCodes = obj.get('pictogramCodes', [])
    param_features_str = array_to_string(param_features)
    pictogramCodes_str = array_to_string(pictogramCodes)

    details = (
        f"化学品名称: {obj.get('chemName', 'N/A')}\n"
        f"危险性类别: {obj.get('riskCategory', 'N/A')}\n"
        f"危险性说明: {obj.get('riskDesc', 'N/A')}\n"
        f"象形图: {pictogramCodes_str}\n"
        f"外观与性状: {obj.get('apperanceShape', 'N/A')}\n"
        f"熔点: {obj.get('meltPoint', 'N/A')}\n"
        f"沸点: {obj.get('boilPoint', 'N/A')}\n"
        f"相对密度: {obj.get('relativeDensity', 'N/A')}\n"
        f"闪点: {obj.get('flashPoint', 'N/A')}\n"
        f"溶解性: {obj.get('solubilty', 'N/A')}\n"
        f"健康危害: {obj.get('healthHazard', 'N/A')}\n"
        f"职业接触限值: {obj.get('careerContactLimit', 'N/A')}\n"
        f"环境危害: {obj.get('environmentHazard', 'N/A')}\n"
        f"急救措施: {obj.get('firstMeasure', 'N/A')}\n"
        f"灭火方法: {obj.get('adviceProjectExtinguish', 'N/A')}\n"
        f"理化特性: {param_features_str}\n"
        f"泄漏措施: {obj.get('leakageMeasure', 'N/A')}\n"
    )
    return details


@mcp.tool()
@rate_limit(lambda: "chemicals_list")  # 速率限制
async def get_chemicals_list_tool(chemName: str, chemCas: str) -> Any:
    """
    Search for chemicals in the NRCC database.

    Args:
        chemName (str): The chemical name to search for (e.g., "滴滴涕", "苯").
        chemCas (str): The CAS number to search for (e.g., "50-29-3", "71-43-2").

    Returns:
        Any: Formatted search results from the NRCC database.

    Example:
        result = await get_chemicals_list_tool(chemName="滴滴涕", chemCas="50-29-3")
    """
    try:
        chemicals_list = await search_chemicals_list(chemName, chemCas)
        formatted_list = await format_chemicals_list(chemicals_list)
        logger.info(f"Chemicals list search successful for: {chemName}")
        return formatted_list
    except Exception as e:
        logger.error(f"Error in get_chemicals_list_tool: {e}")
        raise


@mcp.tool()
@rate_limit(lambda: "chemical_detail")  # 速率限制
async def get_chemical_detail_tool(chem_id: str) -> Any:
    """
    Retrieve detailed information for a specific chemical from the NRCC database.

    Args:
        chem_id (str): The chemical ID to retrieve details for (e.g., "82861C0E-1391-4E10-8AAF-6C342C59EB92").

    Returns:
        Any: Detailed chemical information including physical properties, hazards, safety measures, etc.

    Example:
        result = await get_chemical_detail_tool(chem_id="82861C0E-1391-4E10-8AAF-6C342C59EB92")
    """
    try:
        chemical_detail = await search_chemical_detail(chem_id)
        formatted_detail = await format_chemical_detail(chemical_detail)
        logger.info(f"Chemical detail retrieved for ID: {chem_id}")
        return formatted_detail
    except Exception as e:
        logger.error(f"Error in get_chemical_detail_tool: {e}")
        raise


def main():
    # Initialize and run the server
    mcp.run(transport = 'streamable-http')
    logging.info("NRCC MCP server is running...")


if __name__ == "__main__":
    # chemicals_list = asyncio.run(search_chemicals_list("滴滴涕"))
    # formatted_list = asyncio.run(format_chemicals_list(chemicals_list))
    # logging.info(formatted_list)

    # chemical_detail = asyncio.run(search_chemical_detail("82861C0E-1391-4E10-8AAF-6C342C59EB92"))
    # formatted_detail = asyncio.run(format_chemical_detail(chemical_detail))
    # logging.info(formatted_detail)
    main()
