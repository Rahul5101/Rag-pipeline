import os
from src_06.utils import load_config
config = load_config()
from google.cloud import discoveryengine_v1 as discoveryengine
service_account = config["credentials"]["service_account_path"]
service_account_path = os.path.abspath(service_account)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
projectId = config["credentials"]["project_id"]
Location = config["credentials"]["location"]
model = config["src"]["reranker"]["model"]
rankingConfig = config["src"]["reranker"]["ranking_config"]

def rerank_with_google(query, docs, projectId, location=Location, return_scores=False):
    client = discoveryengine.RankServiceClient()

    ranking_config = client.ranking_config_path(
        project=projectId,
        location=location,
        ranking_config=rankingConfig,
    )

    records = []
    for i, doc in enumerate(docs):
        records.append(
            discoveryengine.RankingRecord(
                id=str(i),
                title=doc.metadata.get("source", f"Doc_{i}"),
                content=doc.page_content
            )
        )

    request = discoveryengine.RankRequest(
        ranking_config=ranking_config,
        model=model,
        top_n=len(docs),
        query=query,
        records=records,
    )

    response = client.rank(request=request)
    ranked_docs = []
    for r in response.records:
        idx = int(r.id)
        doc = docs[idx]
        if return_scores:
            doc.metadata["score"] = r.score
        ranked_docs.append(doc)

    return ranked_docs

