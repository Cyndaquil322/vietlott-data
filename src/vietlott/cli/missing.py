import math

import click
import pandas as pd
import pendulum
from loguru import logger

from vietlott.config.map_class import map_class_name
from vietlott.config.products import ProductConfig, product_config_map
from vietlott.crawler.products import BaseProduct


@click.command()
@click.pass_context
@click.argument("product")
@click.option("--limit", default=20)
def detect_missing_data(ctx, product, limit):
    """
    detect_missing_data and run if needed
    :param ctx: context
    :param product: product to run
    :param limit: number of pages to run
    :return:
    """
    if product not in product_config_map:
        click.echo(f"Error:: Product must in product_map: {list(product_config_map.keys())}", err=True)
        ctx.exit(1)
    click.echo(f"product={product}, limit={limit}")

    product_cfg: ProductConfig = product_config_map[product]
    df = pd.read_json(product_cfg.raw_path, lines=True)
    if df.empty or "id" not in df.columns:
        logger.info(f"Empty dataset or missing 'id' column for {product}")
        return

    df["id"] = df["id"].astype(str).str.replace("#", "").astype(int)
    df = df.sort_values("id").drop_duplicates(subset=["id"]).reset_index(drop=True)
    df["id_next"] = df["id"].shift(-1)
    df["diff"] = df["id_next"] - df["id"]

    df_missing = df[df["diff"] > 1].copy()
    if df_missing.empty:
        logger.info(f"No missing draws detected for {product}. Dataset is 100% continuous.")
        return

    last_id = df["id"].max()
    df_missing["index"] = df_missing["id"].apply(lambda x: (last_id - x) / product_cfg.page_size)
    df_missing["index_next"] = df_missing["id_next"].apply(lambda x: (last_id - x) / product_cfg.page_size)
    df_missing_process = df_missing.head(limit)

    logger.info(f"Found {len(df_missing_process)} missing interval(s) for {product}:\n" + df_missing_process[["date", "id", "id_next", "diff", "index", "index_next"]].to_markdown())

    run_date = pendulum.now(tz="Asia/Ho_Chi_Minh").to_date_string()
    product_obj: BaseProduct = map_class_name[product]()
    for row in df_missing_process.itertuples():
        if (row.index - row.index_next) > 50:
            step = 20
            for i in range(int(math.floor(row.index_next)), int(math.ceil(row.index)), step):
                product_obj.crawl(
                    run_date_str=run_date,
                    index_from=i,
                    index_to=i + step,
                )
        else:
            product_obj.crawl(
                run_date_str=run_date,
                index_from=int(math.floor(row.index_next)),
                index_to=int(math.ceil(row.index)),
            )


if __name__ == "__main__":
    detect_missing_data()
