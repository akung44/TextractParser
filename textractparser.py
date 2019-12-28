import boto3
import re
import pandas as pd
import numpy as np

# Document
s3BucketName = "receiptscanclientimagepipeline"
documentName = "StandardItemized.jpg"

"""
# Amazon Textract client
textract = boto3.client('textract')
s3client=boto3.client('s3')


# Call Amazon Textract
response = textract.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': documentName
        }
    })

#print(response)
"""

products=[]
for item in response["Blocks"]:
    if item["BlockType"] == "LINE":
        products.append(item["Text"])

items=[]
costs=[]
numberless=[]

# Get possible items and prices
for text in range(len(products)):
    try:
        if "$" in products[text+1]:
            items.append(products[text])
            items.append(products[text+1])
    except IndexError:
        pass

prodprice=[]
actualprod=[]
unique = []
[unique.append(x) for x in items]
for i in range(len(unique)):
    if "$" in unique[i]:
        prodprice.append(unique[i])
    else:
        try:
            int(unique[i])
        except ValueError:
            actualprod.append(unique[i])
# Separate prices and possible items
finalproducts=[]
position=0

# Separate items from total, taxes, and credit cards
for product in actualprod:
    try:
        item=product.upper()
        creditnumbers=re.findall("\d+(?:\.\d+)", product)
        if "TOTAL" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "/" in item:
            prodprice.remove(prodprice[position])
            position-=1            
        elif "PURCHASE" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "TAX" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "XXX" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "###" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "VISA" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "AMT" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif "AMOUNT" in item:
            prodprice.remove(prodprice[position])
        elif "BALANCE" in item:
            prodprice.remove(prodprice[position])
            position-=1
        elif int(creditnumbers[0])>1000:
            prodprice.remove(prodprice[position])
            position-=1
        else:
            finalproducts.append(product)
        position+=1        
    
    except IndexError:
        position+=1
        finalproducts.append(product)
        pass
    
# To fix wrong things in the cost list
finalproductcost=[]

for possibleprice in prodprice:
    item=possibleprice.upper()
    creditnumbers=re.findall("\d+(?:\.\d+)?", possibleprice)[0]
    try:
        if "TOTAL" in item:
            pass
        elif "PURCHASE" in item:
            pass
        elif "TAX" in item:
            pass
        elif "XXX" in item:
            pass
        elif "###" in item:
            pass
        elif "VISA" in item:
            pass
        elif "AMT" in item:
            pass
        elif "AMOUNT" in item:
            pass
        elif "BALANCE" in item:
            pass
        elif "/" in item:
            pass
        elif float(creditnumbers)>1000:
            pass
        else:
            price1=re.findall("\$\d+(?:\.\d+)?", possibleprice)[0]
            price2=re.findall("\d+(?:\.\d+)?", possibleprice)[0]
            try:
                float(price2)
                finalproductcost.append(price1)
                pos=prodprice.index(possibleprice)
                nocost=possibleprice.replace(price1, "")
                if nocost[0].isalpha()==True:
                    finalproducts.insert(pos, nocost)
            except ValueError:
                pass
        
    except IndexError:
        pass

# Get rid of quantities
cleaningquant=[]
for firstval in finalproducts:
    if firstval[0].isalpha()==False:
        secondval=firstval[1:].lstrip()
        cleaningquant.append(secondval)
        continue

    cleaningquant.append(firstval)

intcosts=[]

# Turn prices into floats
for entries in finalproductcost:
    try:
        errors=entries.replace(" ", "")
        price=re.findall("\$\d+(?:\.\d+)?", entries)
        dollarvalue=price[0]
        finalvalue=float(dollarvalue.replace("$",""))
        intcosts.append(finalvalue)
    except IndexError:
        intcosts.append(entries)

print(cleaningquant)
print(intcosts)

# Get JSON file
fullprodlist=np.asarray(cleaningquant)
fullcostlist=np.asarray(intcosts)

df = pd.DataFrame()
df["Item"]=fullprodlist
df["Price"]=fullcostlist

jsfile=df.to_json(orient='index')
