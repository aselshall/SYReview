def Extract_Lines(period,topic,searchwords,Opt=0):
    
    import re 
    import pandas as pd 
    
    #[1] Input txt file to extract text from 
    filename='records_'+topic+period+'.csv'
    records=pd.read_csv(filename).fillna('NONE')
    nrecords=len(records)
    print('Reading from "{}": Period {} has {} records about "{}"' 
      .format(filename, period,nrecords,topic))

    #[2] Output txt file for saving extracted text 
    outputfile='ExtractedText'+topic+period+'.csv'
    df=pd.DataFrame({key: [] for key in ['ExtractedText']}) 
    
    #[3] Loop for all articles
    for m in range(len(records)):
        #[3.1] Split abstract to lines
        #text=records.loc[m,'Abstract']
        text=records.loc[m,'Abstract']+ ' '+ records.loc[m,'Title']
        text=re.sub(r'[\d]\.[\d]', r' ',text)
        text=re.sub('i\.e\.', 'ie',text)
        text=re.sub('e\.g\.', 'eg',text)
        text=re.sub('st\.', 'st',text)
        text=re.sub('b\.v\.', 'bv',text)
        text=re.sub('\. ', '\n ',text) 
        text=text.split('\n')

        #[3.2] Extract text by looping the abstract text
        txt=[]
        for searchword in searchwords:
            for n in range(len(text)):
                if text[n].count(searchword)>0:
                    if Opt ==0:
                        txt.append(text[n])
                    elif Opt==1:            
                        if len(text)==1:
                            txt.append(text[0])
                        elif n==0 and len(text)>1:
                            txt.append(text[0]+text[1])
                        elif n+1==len(text):
                            txt.append(text[n-1]+text[n])
                        else:
                            txt.append(text[n-1]+text[n]+text[n+1])
        df.loc[m,'ExtractedText']='.'.join(txt)

        #[3.3] Saving extracted text to a file
        df.to_csv(outputfile, index=False)
        
    print('Extracted lines saved to "{}"'.format(outputfile))
    
    return outputfile, nrecords
    
def Index_Records(Topics,topics):
    
    import pandas as pd 
    from SYWorkflow import Extract_Records
    
    #Make dictionary for frequence
    Num=['MatchingRecords2010','MatchingRecords2020', 'TotalRecords2010','TotalRecords2020']
    val=[0]*len(Topics)
    Count = pd.DataFrame({num:val for n, num in enumerate(Num)},index=Topics)
    
    #Index records 
    for n, topic in enumerate(Topics):
        MatchingRecords2010,MatchingRecords2020, TotalRecords2010,TotalRecords2020,CountKeywords=Extract_Records(topic,topics[topic])
        Count.loc[topic,:]=[MatchingRecords2010,MatchingRecords2020, TotalRecords2010,TotalRecords2020]
    Count.loc[:,'NormalizedFrequency2010']=Count.loc[:,'MatchingRecords2010']/Count.loc[:,'TotalRecords2010']
    Count.loc[:,'NormalizedFrequency2020']=Count.loc[:,'MatchingRecords2020']/Count.loc[:,'TotalRecords2020']
    return Count 


def Extract_Records(topic,keywords,prnt=0,inputfile='recordsFrom2001.csv',outputopition=0):
    
    """Extract records about the topic you are interested in 
    Parameters:
    -----------
   topic : string
        Topic of interest 
   keywords: list of strings
        Keywords that define your topic 
                
    Return:
    --------
    MatArtNum2010 : Matching records 2010
    ArtNum2010    : All records 2010
    MatArtNum2020 : Matching records 2020
    ArtNum2020    : All records 2020
    records dataframe saved to 'recordsTopic2010.csv'
                                'recordsTopic2020.csv'
    """
    
    import pandas as pd 
    import re
    #Load all records infromation file
    #inputfile='recordsFrom2001.csv'
    records=pd.read_csv(inputfile).fillna('NONE')
    if prnt==1:
        print('Reading',len(records),'records from',inputfile)
    if prnt>1:        
        print(topic,'keywords are',keywords)

    #Count occurance per article 
    if outputopition<3:
        records.loc[:,topic]=0

    
    #Format of output file
    keys=['Author','Year','Journal','Title','Abstract']
    df2010=pd.DataFrame({key: [] for key in keys})    
    df2020=pd.DataFrame({key: [] for key in keys}) 

    #All records in a period counter 
    ArtNum2010=0      
    ArtNum2020=0

    #Matching records in a period counter
    MatArtNum2010=0  
    MatArtNum2020=0 
    
    #Exact match list
    ExactMatchList=['culture','cultural']
    
    #Count all keywords
    if outputopition==3:
            CountKeywords=[0]*len(keywords)
    else:
            CountKeywords=[]
            
            
    #Extract articels with search word and split into two periods
    for m in range(len(records)): 

        #Update number of records per period
        if records.loc[m,'Year']<2011:
            ArtNum2010=ArtNum2010+1 
        else:
            ArtNum2020=ArtNum2020+1 

        #Search for keywords in abstract
        text=records.loc[m,'Abstract']+ ' '+ records.loc[m,'Title']
        count=0
        for nword, word in enumerate(keywords):
            if word in ExactMatchList:  
                searchword=sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text)) 
                count= count+ searchword
            else:
                searchword=text.count(word)
                
            #Topic counter
            count=count+searchword
            
            #keyword counter 
            if outputopition==3: 
                searchword=min(searchword,1)
                CountKeywords[nword]=CountKeywords[nword]+searchword

        #Topic flag 
        if outputopition<3:
            records.loc[m,topic]=count

        #Extract records with matching keywords and split into to periods
        if count>0:
            if records.loc[m,'Year']<2011:
                df2010.loc[MatArtNum2010]=records.loc[m]
                MatArtNum2010=MatArtNum2010+1  
            else:
                df2020.loc[MatArtNum2020]=records.loc[m]
                MatArtNum2020=MatArtNum2020+1  

    #Data correction             
    df2010['Year'] = df2010.Year.astype('int64')   
    df2020['Year'] = df2020.Year.astype('int64')   
    records['Year'] = records.Year.astype('int64')  
    
    #Save results to file    
    if outputopition>0:
        df=pd.concat([df2010,df2020]).sort_values('Year')
        df.to_csv('records'+topic+'.csv', index=False)
    
    if outputopition>1:   
        periods=['2010','2020']
        for n, period in enumerate(periods): 
            file='records'+topic+period+'.csv'
            if n==0:
                df2010.to_csv(file, index=False)
                if prnt>2:
                    print('Period 2010 has {} of {} records about `{}` saved to {}'
                          .format(MatArtNum2010,ArtNum2010,topic,file))
            elif n==1:
                df2020.to_csv(file, index=False)
                if prnt>2:
                    print('Period 2020 has {} of {} records about `{}` saved to {}'
                          .format(MatArtNum2020,ArtNum2020,topic,file))

    
    #Save mail file with topic index 
    if outputopition<3:
        records.to_csv(inputfile, index=False)
        
    #Return the follow    
    MatchingRecords2010=MatArtNum2010
    MatchingRecords2020=MatArtNum2020
    TotalRecords2010=ArtNum2010
    TotalRecords2020=ArtNum2020
    #CountKeywords=pd.Series({key:Count[4][n] for n, key in enumerate(keywords)}, name='recordsCount')
    #CountKeywords.index.name = 'Keyword'
    return MatchingRecords2010,MatchingRecords2020, TotalRecords2010,TotalRecords2020,CountKeywords 





def Read_exportlist(opition=0):

    """Read exported data and extract relevent information
    
    Parameters:
    -----------
    opition (opitional): integer / string
       opition 0              for 'exportlist1771.txt' with data: SY(1346) + GW sustainbility(148) + Sustainable GW(277)
       opition 1              for 'exportlist1494.txt' with data: SY(1346) + GW sustainbility(148)
       opition 2              for 'exportlist1346.txt' with data: SY(1346)
       opition 'filename.txt' for  any other dataset          
    Return:
    --------
    records dataframe saved to 'recordsAll.csv'
                                'recordsFrom2001.csv'
                                'recordsPre2001.csv'
    """
    
    import re                              #Regular expression
    import pandas as pd 
    
    #Select file
    if opition==0:
        rawfilename='exportlist1771.txt'
    elif opition==1:
        rawfilename='exportlist1494.txt'
    elif opition==2:
        rawfilename='exportlist1346.txt'
    else:
        rawfilename=opition 
   
    #Import records data
    file = open(rawfilename, 'r'); text = file.read(); file.close()
    recordsRaw= re.split('TY  -',text)[1:]
    print('Reading', len(recordsRaw), 'records from' ,rawfilename)
    patterns=['AU  -','PY  -', 'T2  -','TI  -','AB  -']
    keys=['Author','Year','Journal','Title','Abstract']
    records=pd.DataFrame({key: [] for key in keys})
    sw='NO_ABSTRACT'

    for m, article in enumerate(recordsRaw):
        for n, pattern in enumerate(patterns):
            if n<3: #Author, Year, Jouranl
                txt=re.split(pattern,article)[1].split('\n')[0].strip() 
                if n==0:
                    txt=txt.split(',')[0].strip() + ' et al.'
            else:   #Title, Abstract
                txt=re.split(pattern,article)
                if len(txt)==1:
                    txt=re.split('TI  -',article)
                txt=txt[1].split('\n')[0].lower().strip()
                txt=re.sub(r'-', ' ',txt)           #remove '-'
                txt=re.sub('ground water','groundwater',txt)
                txt=re.sub('surface water','surfacewater',txt)
                txt=re.sub('stake holder','stakeholder',txt)
                txt=re.sub('land use','landuse',txt)
                txt=re.sub('water budget','waterbudget',txt)
                txt=re.sub('over exploitation','overexploitation',txt)
                txt=re.sub('water balance','waterbalance',txt)
                txt=re.sub('initial condition','initialcondition',txt)
                txt=re.sub('boundary conditions|boundary condition','boundarycondition',txt)
                txt=re.sub('flow directions|flow direction','flowdirection',txt)
                txt=re.sub('adaptive management','adaptivemanagement',txt)    
                txt=re.sub('gcms|gcm|glocal circulation models|glocal circulation model','GCM',txt)
                txt=re.sub('sensitivity analysis','sensitivityanalysis',txt) 
                txt=re.sub('water table','watertable',txt) 
            records.loc[m,keys[n]]=txt 

    #[2] Save and load data
    filename='recordsAll.csv'
    records.to_csv(filename, index=False)
    print('Done saving', records.shape, 'matrix with',keys,'to',filename)

    #Extract articels with search word and split into two periods
    records=pd.read_csv(filename).fillna(sw)
    print('Reading',len(records),'records from',filename)
    keys=['Author','Year','Journal','Title','Abstract']
    dfYes=pd.DataFrame({key: [] for key in keys})    
    dfNo=pd.DataFrame({key: [] for key in keys}) 
    countYes=0
    countNo=0 
    for m in range(len(records)): 
        text=records.loc[m,'Abstract']
        if text.count(sw)==0:
            if records.loc[m,'Year']>2000:
                dfYes.loc[countYes]=records.loc[m]
                countYes=countYes+1  
            else:
                dfNo.loc[countNo]=records.loc[m]
                countNo=countNo+1    
    dfYes['Year'] = dfYes.Year.astype('int64')   
    dfNo['Year'] = dfNo.Year.astype('int64')   

    #Save results to file    
    periods=['Yes','No']
    for n, period in enumerate(periods): 
        if n==0:
            file='recordsFrom2001.csv'
            dfYes.to_csv(file, index=False)
            print('{} records saved to {}'.format(countYes,file))
        elif n==1:
            file='recordsPre2001.csv'
            dfNo.to_csv(file, index=False)
            print('{}  records saved to {}'.format(countNo,file))

def axislabel(ax,rects,xpos):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """
    
    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                '{}'.format(height), ha=ha[xpos], va='bottom')

        
def KeyworkExtract(Topics,topics,Flag,Save,Disp):
    
    #Load all articles
    import pandas as pd 
    filename='recordsFrom2001.csv'
    records=pd.read_csv(filename).fillna('NONE')

    for topic in Topics:
        records.loc[records.loc[:,topic]>0,topic]=1

    #Flag [0] and [1] for non-matching and matching records
    index=Flag*len(topics)

    #Filter by topics
    name='records' 
    for n, topic in enumerate(topics):  
        records=records.loc[records.loc[:,topic]==index[n],:]
        if index[n]==0:
            name=name+'_No'+topic 
            if Disp>0:
                print(len(records),'records after remvoing',topics[n],'records') 
        elif index[n]==1:
            name=name+'_'+topic
            if Disp>0:
                print(len(records),'records after remvoing non',topics[n],'records') 
                


    #Save articles to a file 
    if Save>0:
        records=records.sort_values(by=['Year'],ascending=False)
        file=name+'.csv'
        records.to_csv(file, index=False)
        print('Save do {}'.format(file))  

    #Save articles to by period a file 
   
    periods=['2010','2020']
    for n, period in enumerate(periods):
        if n==0:
            Period=records[records['Year']<=2010]
        elif n==1:
            Period=records[records['Year']>2010]   
        file=name+period+'.csv'
        print('Period {} has {} of {} records about {}'
       .format(period,len(Period),len(records),topics))        
        if Save>1:
            Period.to_csv(file, index=False)
            print('Save to {}'.format(file))  
            #display(Period.head(n=3)) 
            
    if Disp>1:            
        display(records)       