import json
import os
from os import listdir
from os.path import isfile, join, dirname

from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from utils.privacy_ner_bert import anonymize_text
from utils.pdftotext_layout import extract_text_with_pdftotext

my_labels = ["CITATION", "ACCOUNTS", "PROVISION", "JURISDICTION", "COURT","INSTRUMENT"]


sample_accordion_data={
    "sections": [
      {
        "clause": "Section 1",
        "text": "This is the content of section 1."
      },
      {
        "clause": "Section 2",
        "text": "This is the content of section 2."
      }
    ]
  }
  


def get_user_pdf(input_filePath):
    # Get the full filename with extension
    filename = os.path.basename(input_filePath)
    
    # Split the filename to remove the original extension
    filename = os.path.splitext(filename)[0]
    filename_without_extension=os.path.splitext(filename)[0]
    userPublicId = "first_1"
    print(input_filePath)

    if os.path.isfile(input_filePath) == False:
        print('No files found')
        resp = jsonify({'message': 'File Not Found!!'})
        resp.status_code = 404
        return resp

    dir = os.path.join(os.path.dirname(__file__) + '/static' + '/highlights/' + userPublicId)
    
    if os.path.isdir(dir) == False:
        print("doesnt exist")
        os.makedirs(dir, exist_ok=True)

    # Use the filename without extension for all derived files
    filepath = join(dir, filename_without_extension + '.json')
    extract_text_file_path = join(dir, filename_without_extension + '_extractedtext.txt')
    saved_anonymized_file = join(dir, filename_without_extension + '_anon.txt')
    saved_hash_file = join(dir, filename_without_extension + '_hash.json')
    isHighlightsAvailable = False
    # data = {}
    # if os.path.isfile(filepath):
    #     print("\nFile exists\n")
    #     with open(filepath, 'r') as json_file:
    #         data = json.load(json_file)
    #         if data['name'] == filename:
    #             isHighlightsAvailable = True
    #             print("Highlights already present for pdf: " + filename)
    #             # response = app.response_class(
    #             #     response=json.dumps({"highlights": data}),
    #             #     status=200,
    #             #     mimetype='application/json',
    #             # )
    #             # return response

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    fp = open(input_filePath, 'rb')
    pages = PDFPage.get_pages(fp)
    check = "Disclosure"
    counter = 0
    id_counter = 0
    proccessed_data = {}
    provision_entities = []
    labels = []
    memory = 0  # memorize how many occurance it has seen.
    prev_text = ""
    current_text = ""
    pageSizesList = []

    entities = []
    labels = []
    full_text = ""

    for page in pages:
        counter += 1
        print('Processing ', counter, 'page...')
        # size=page.mediabox
        # print(size)
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x1, y0_orig, x2, y1_orig, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text(
                )
                y1 = page.mediabox[3] - y1_orig
                y2 = page.mediabox[3] - y0_orig

                text = text.strip()
                # textSegmentation(text)
                # Append extracted text to the full_text variable
                full_text += text + "\n"  # Adding a newline for readability
                print("full_text",full_text)
                ## Annonymise Text ##

                # anonymized_text = anonymize_text(text,input_filePath,saved_anonymized_file,saved_hash_file)
                anonymized_text=""
                json_dump = []
        
                id_counter += 1
                jsont = {
                    "comment": {
                            "emoji": "",
                            # "text": most_common[0][0],
                            "anonymized_text": anonymized_text,

                            "classifier_score": 0
                        },
                        "content": {
                            "text": text,
                            "entities": "ents",
                        },
                        "id": str(id_counter),
                        "position": {
                            "boundingRect": {

                                "x1": x1,
                                "y1": y1,
                                "x2": x2,
                                "y2": y2,
                                "height": page.mediabox[3],
                                "width": page.mediabox[2]
                            },
                            "pageNumber": counter,
                            "rects": [
                                {

                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2,
                                    "height": page.mediabox[3],  # get height of each page
                                    "width": page.mediabox[2]  # get width of each page

                                }
                            ]
                        }
                    }
                arr = proccessed_data.setdefault(filename, [])
                current_text = jsont["content"]["text"]
                if prev_text == current_text:
                    memory += 1
                elif prev_text != current_text:
                    memory = 0  # increment memory
            
                jsont["comment"]["classifier_score"] = (memory)
                prev_text = current_text
                current_text = ""
            
                arr.append(jsont)

    newFile = {}
    graphData = {}
    graphDir = os.path.join(os.path.dirname(__file__) + '/static'+ '/graphData/' + userPublicId)
    if os.path.isdir(graphDir) == False:
        print("doesnt exist")
        os.makedirs(graphDir, exist_ok=True)
    if filename in proccessed_data:
        newFile = {"highlights": proccessed_data[filename], "name": filename, "entities": entities, "sections": sample_accordion_data['sections']}
        print('THE NO. OF LABELS IN THIS PDF', len(labels))
        print('THE NO. OF ENTITIES IN THIS PDF', len(entities))
        print('entities before graph call',entities)
        print('labels before graph call',labels)
        print('type entities',type(entities))
        print('type labels',type(labels))

        filenamelist = [filename, filename, filename, filename, filename,filename]
        nodes = [{"id": x} for x in (entities + my_labels)]
        nodes2 = [{"id": filename}]
        nodes = (nodes + nodes2)
        centerlabel = [{"source": filenamelist, "target": my_labels} for filenamelist, my_labels in
                       zip(filenamelist, my_labels)]
        # print(centerlabel)
        labels = [{"source": label, "target": target} for label, target in zip(labels, entities)]
        labels = (labels + centerlabel)
        print(type(entities))
        # print(nodes)
        # print(labels)
        graphData = {
            "fileName": filename,
            "nodes": nodes,
            "links": labels
        }
    with open(join(graphDir, filename + '.json'), 'w') as graph_file:
        json.dump(graphData, graph_file)

    with open(filepath, 'w') as json_file:
        json.dump(newFile, json_file)
    


    extracted_text,layout_text_file = extract_text_with_pdftotext(input_filePath,extract_text_file_path)
    anonymized_text = anonymize_text(extracted_text,input_filePath,saved_anonymized_file,saved_hash_file)

    return {
    "extracted_text": extracted_text,
    "layout_text_file": layout_text_file,
    "anonymized_text": anonymized_text,
    "saved_anonymized_file": saved_anonymized_file,
    "saved_hash_file": saved_hash_file,
    "newFile": newFile
        }
        

    # response = app.response_class(
    #     response=json.dumps({"highlights": newFile}),
    #     status=200,
    #     mimetype='application/json',
    # )

  

    # if inbound:
    #     return full_text

    # return response


# if __name__ == "__main__":
#     get_user_pdf()