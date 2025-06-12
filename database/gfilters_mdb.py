import pymongo
from info import DATABASE_URI, DATABASE_NAME
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    mycol = mydb[str(gfilters)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }

    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except:
        logger.exception('Some error occurred!', exc_info=True)


async def find_gfilter(gfilters, name):
    mycol = mydb[str(gfilters)]
    query = mycol.find({"text": name})

    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            alert = file.get('alert', None)
            return reply_text, btn, alert, fileid
    except:
        logger.exception("Error during find_gfilter")
        return None, None, None, None


async def get_gfilters(gfilters):
    mycol = mydb[str(gfilters)]
    texts = []
    query = mycol.find()
    try:
        for file in query:
            texts.append(file['text'])
    except:
        logger.exception("Error during get_gfilters")
    return texts


async def delete_gfilter(message, text, gfilters):
    mycol = mydb[str(gfilters)]
    myquery = {'text': text}
    query = mycol.count_documents(myquery)

    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`' deleted. I'll not respond to that gfilter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that gfilter!", quote=True)


async def del_allg(message, gfilters):
    if str(gfilters) not in mydb.list_collection_names():
        await message.edit_text("Nothing to Remove !")
        return

    mycol = mydb[str(gfilters)]
    try:
        mycol.drop()
        await message.edit_text("All gfilters have been removed!")
    except:
        await message.edit_text("Couldn't remove all gfilters!")
        logger.exception("Error during del_allg")


async def count_gfilters(gfilters):
    mycol = mydb[str(gfilters)]
    count = mycol.count_documents({})
    return False if count == 0 else count


async def gfilter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count_documents({})
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount
