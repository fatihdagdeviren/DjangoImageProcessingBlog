from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import cv2
import views.Methods as methods
import uuid
from polls.models import *
from django.contrib.auth.decorators import login_required
import datetime


import views.Copy_Move_Forgery_Folder.Sift_Sift_KNN as sift
import views.Copy_Move_Forgery_Folder.Sift_Surf_KNN as surf
import views.Copy_Move_Forgery_Folder.Sift_Daisy_KNN as daisy
import views.Copy_Move_Forgery_Folder.Sift_Freak_KNN as freak
import views.Copy_Move_Forgery_Folder.SIFT_LTP_ as ltp
import views.Panorama_Maker.Panorama_Maker as panoramaMaker
statifFilePath = 'static/Temp/'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    """Renders the home page."""
    post_index = Post.objects.filter(controllerName='Index').first()
    return render(request, 'index.html',{'post':post_index,'user':request.user})

def ImageProcessing(request):
    return render(request, 'ImageProcessing.html')

def Contact(request):
    return render(request, 'Contact.html')

def DigitRec(request):
    post_DigitRec = Post.objects.filter(controllerName="DigitRec").first()
    if request.method=="GET":
        return render(request, 'DigitRec.html',{'post':post_DigitRec})
    if request.method=="POST":
        try:
            selectedFile = request.FILES['input-b1']
            myfile = saveImageToUrl('DigitRec', selectedFile)
            #extension  = request.POST.get('extension')
            if myfile is not None:
                im,text = methods.hogIsle('Resources/digits_cls.pkl',myfile)
                pathToSave = 'static/Temp/Edited_'+  str(uuid.uuid4()) + '_' + selectedFile.name
                methods.saveImageToFile(pathToSave, im)
                return render(request,'DigitRec.html',{
                'uploaded_file_url': myfile , 'edited_file_url': pathToSave, 'converted_text':text,'post':post_DigitRec
                 })
        except BaseException as e:
            print(str(e))
            pass
    return render(request, 'DigitRec.html')

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        redirectPage = request.POST.get('redirect')
        fs = FileSystemStorage()
        ipAdress = get_client_ip(request)
        myfile.name = redirectPage+'_'+ myfile.name
        uploadUrl = 'static/Temp/'+ myfile.name
        filename = fs.save(uploadUrl, myfile)
        uploaded_file_url = fs.url(myfile.name)
        try:
            return render(request, '{}.html'.format(redirectPage), {
                'uploaded_file_url': uploaded_file_url
            })
        except BaseException as e:
            print(str(e))

def saveImageToUrl(controllerName,myfile):
    try:
        fs = FileSystemStorage()
        uploadUrl = statifFilePath + controllerName +'_'+ myfile.name
        filename = fs.save(uploadUrl, myfile)
        return filename
    except BaseException as e :
        return None

def cmfd(request):
    cmfdPost = Post.objects.filter(controllerName = 'Cmfd').first()
    cmfdMethods = list(Code.objects.filter(codeGroup=1 , visible=True))
    if request.method=="GET":
        return render(request, 'Cmfd.html',{'Post':cmfdPost,'CmfdMethods':cmfdMethods})
    if request.method=="POST" and  request.FILES['input-b1']:
        try:
            selectedFile = request.FILES['input-b1']
            myfile = saveImageToUrl('Cmfd',selectedFile)
            method = request.POST.get('hdnCmfd')
            ipAdress = get_client_ip(request)
            # extension  = request.POST.get('extension')
            if myfile is not None:
                myTempFile =  myfile
                if method == '1001' or method is None or method == '':
                    forgedImage,forgedRansacImage = sift.sift_sift_knn(myTempFile,0.7,12)
                elif method == '1002':
                    forgedImage,forgedRansacImage = daisy.sift_daisy_knn(myTempFile,0.7,12)
                elif method == '1003' :
                    forgedImage, forgedRansacImage = surf.sift_surf_knn(myTempFile, 0.7, 12)
                elif method == '1004':
                    forgedImage, forgedRansacImage = freak.sift_freak_knn(myTempFile, 0.7, 12)
                elif method == '1005' :
                    forgedImage, forgedRansacImage = ltp.sift_ltp(myTempFile, 15, 0.7, 8,ThresholdForGLCM=None)
                pathToSave = 'static/Temp/CMFD_Edited_'+str(uuid.uuid4())+'_'+ selectedFile.name
                pathToSaveRANSAC = 'static/Temp/CMFD_Edited_RANSAC_' + str(uuid.uuid4()) + '_' + selectedFile.name
                methods.saveImageToFile(pathToSave,forgedImage)
                methods.saveImageToFile(pathToSaveRANSAC,forgedRansacImage)
                return render(request, 'Cmfd.html', {
                    'uploaded_file_url': myfile, 'edited_file_url': pathToSave,'edited_file_url2': pathToSaveRANSAC,'Post':cmfdPost,'CmfdMethods':cmfdMethods
                })
        except BaseException as e:
            print(str(e))
            pass
    return render(request, 'Cmfd.html')

def ImageRetrieval(request):
    if request.method=="GET":
        return render(request, 'ImageRetrieval.html')
    if request.method=="POST":
        try:
            myfile = request.POST.get('myfile')  # this is my file
            keyword = request.POST.get('keyword')
            ipAdress = get_client_ip(request)
            sonuclar = []
            if myfile is not None:
                myTempFile = statifFilePath + myfile
                pathToSave = 'static/Temp/Edited_' + ipAdress + '_' + str(uuid.uuid4()) + '_' + myfile
                # burada google ile resimleri alicam ilk olarak
                resimler_forRetrieval = methods.getPicturesFromGoogleCustomSearch(keyword)
                if resimler_forRetrieval is not None and len(resimler_forRetrieval)>0:
                    image = cv2.imread(myTempFile)
                    for retrievalImage in resimler_forRetrieval:
                        matches,matchImage = methods.findMatchesWithSIFT(image,retrievalImage)
                        if len(matches)>0:
                            retrievalImage = cv2.resize(matchImage, (200, 200))
                            sonuclar.append([matches,retrievalImage])
                countForPath = 1
                imagePaths=[]
                for sonuc in sonuclar:
                    pathToSave = 'static/Temp/Edited_'+ str(countForPath) +'_'+ ipAdress + '_' + str(uuid.uuid4()) + '_' + myfile
                    cv2.imwrite(pathToSave,sonuc[1])
                    imagePaths.append(pathToSave)
                return render(request, 'ImageRetrieval.html', {
                    'uploaded_file_url': myfile, 'retrievalImages': imagePaths
                })
        except BaseException as e:
            print(e)
            pass
        return render(request, 'ImageRetrieval.html')

def PanoramaCreator(request):
    panorama_Inputs = Post.objects.filter(controllerName="PanoramaCreator").first()
    if request.method == "GET":
        return render(request,'PanoramaCreator.html',{'post':panorama_Inputs})
    elif request.method == "POST":
        selectedFiles = request.FILES.getlist('input-b1')
        allowedFiles = list(filter(lambda x: x.content_type in ['image/jpeg','image/png','image/jpeg']  ,selectedFiles))
        if allowedFiles.count == 0:
            return render(request, 'PanoramaCreator.html', {'post': panorama_Inputs})
        else:
            stitcher = panoramaMaker.Stitcher()
            images = []
            for file in allowedFiles:
                myfile = saveImageToUrl('PanoramicImage', file)
                images.append(cv2.imread(myfile))
            result,vis = stitcher.stitch([images[0],images[1]],showMatches=False)
            pathToSave = 'static/Temp/PanoramaCreator_Edited_' + str(uuid.uuid4()) + '_' + allowedFiles[0].name
            methods.saveImageToFile(pathToSave, result)
    return render(request, 'PanoramaCreator.html', {'post': panorama_Inputs,'edited_file_url': pathToSave})

#region LoginRegion

@login_required
def PostEntry(request):
    postList = list(Post.objects.all())
    if request.method == "GET":
        return render(request, 'PostEntry.html', {'postList': postList})
    elif request.method == "POST":
        try:
            p = Post.objects.filter(controllerName= request.POST.get('txtControllerName')).first()
            if p is None:
                p = Post()
            p.title = request.POST.get('txtPostTitle')
            p.content = request.POST.get('postContent')
            p.controllerName = request.POST.get('txtControllerName')
            p.lastUpdate = datetime.datetime.now()
            p.save()
        except BaseException as e:
            print(e)
            pass
        postList = list(Post.objects.all())
        return render(request, 'PostEntry.html', {'postList': postList})

@login_required
def GetPost(request):
    from django.http import JsonResponse
    if request.method == 'GET':
        postId = request.GET.get('id')
        selectedPost = Post.objects.filter(id = postId).first()
        # JsonResponse(dict(genres=list(Genre.objects.values('name', 'color'))))
        return JsonResponse({'content':selectedPost.content,'title':selectedPost.title,'controllerName':selectedPost.controllerName},safe=False)

#endregion



