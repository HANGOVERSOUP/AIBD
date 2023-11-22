import React, { use, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Side_bar from "../../newcomp/global_side_bar";
import Top_select from "../../newcomp/global_select_que";
import FullFeaturedCrudGrid from "../../newcomp/editnet_edit_whole";

export default function Home() {
  const [csvstatus, setCsvStatus] = useState(true);
  const router = useRouter();

  if (router.query.data===undefined){
      router.query.data = "LG_gram_data"
  }
  const [receivedData,setreceivedData]=useState(router.query.data);

  // 모델실행버튼클릭이벤트
  const runmodel = async (selectfile) => {
    console.log("selectfilaaae",selectfile);
  };

  // 파일명변동이벤트
  const filechanged = async (selectfile) => {
    if(selectfile!=null){
      console.log("변동",selectfile.value);
      setreceivedData(selectfile.value);
    }
  };

  const i=2;
  const page=3;
  return (
    //1번 프레임 
    <div id='outter_frame1'>
      {/* 왼쪽 바 */}
      <div id ='left_bar'>
        <Side_bar index={i}/>
      </div>
      {/* 2번 프레임 */}
      <div id='outter_frame2'>
          {/* <TopLabel activeStep={activeStepVal}/> */}
          <Top_select method2={filechanged} method={runmodel} page={page} routed={receivedData}/>
          

          {/* 메인: 선택지 , 차트내용 등 */}
          <div id='main_frame' className='visualize_div'>
            {/* <AuthCheck> */}
            <div>
              <div id='rec'>
                  {/* <p>현재 설문 : {receivedData2}</p> */}
              </div>


              <div id='csvview' > 
                  {/* {csvstatus && (
                      <DynamicTable data={receivedData2}/>
                  )} */}
                  {csvstatus && (
                      <FullFeaturedCrudGrid file={receivedData}/>
                  )}
              </div>
            </div>
            {/* </AuthCheck> */}
            {/* 메인: 선택지 , 차트내용 등 */}              
          </div>
      </div>
    </div>
  );
}
