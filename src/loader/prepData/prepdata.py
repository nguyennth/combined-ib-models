"""Load data from brat format and process for entity, trigger, relation, events."""

from loader.prepData.brat import brat_loader
from loader.prepData.sentence import prep_sentence_offsets, process_input
from loader.prepData.entity import process_etypes, process_tags, process_entities


def prep_input_data(files_fold, params):
    # load data from *.ann files
    triggers0, entities0, relations0, sentences0 = brat_loader(files_fold, params)

    # sentence offsets
    sentences1 = prep_sentence_offsets(sentences0)
    if 'pipeline_text_data' in params:
        sent_words = []
        for pmid in sentences0:
            doc_data = params['pipeline_text_data'][pmid]
            for sent, pipe_sent in zip(sentences1['doc_data'][pmid], doc_data):
                sent['words'] = pipe_sent['words']
                sent_words.append(sent['words'])
                sent['offsets'] = pipe_sent['offsets']
        sentences1['sent_words'] = sent_words

    # entity
    entities1 = process_etypes(entities0)  # all entity types
    triggers1 = process_etypes(triggers0)  # all trigger types
    terms0 = process_tags(entities1, triggers1)  # terms, offset, tags, etypes
    input0 = process_entities(entities1, triggers1, sentences1, params, files_fold)

    # prepare for training batch data for each sentence
    input1 = process_input(input0, entities0, relations0, params, files_fold)

    #check if we miss any gold entities            
    for doc_name, doc in sorted(input0.items(), key=lambda x: x[0]):
        # if doc_name == '0098':
        #     print('Debug')
        entities = set()
        num_entities_per_doc = 0
        for sentence in doc:
            eids = sentence["eids"]
            entities |= set(eids)
            num_entities_per_doc += len(eids)

        full_entities = set(entities1["pmids"][doc_name]["ids"])
        diff = full_entities.difference(entities)
        if diff:
            print("Missing gold entity: ", doc_name, sorted(diff, key=lambda _id: int(_id.replace("T", ""))))

    return {'entities': entities1, 'triggers': triggers1, 'terms': terms0,
            'sentences': sentences1, 'input': input1}
