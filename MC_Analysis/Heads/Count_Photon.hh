#ifndef COUNT_PHOTON_HH
#define COUNT_PHOTON_HH
//CPP
#include <iostream>
#include <fstream>
//ROOT
#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TCanvas.h>
#include <TLegend.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined
#include "./Base_Functions.hh"

// 根据PMT来统计Cali、Test、Con的光子数。
// Con会用反射率进行修正
Double_t Count_PMT_Photon(Int_t PMT, std::string File_Path, std::string Pic_Dir, std::string strings, Int_t Wavelength)
{
    // std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test.root";
// Open the file
    TFile *file = new TFile(File_Path.c_str());
    TTree *sim_truth = (TTree*) file->Get("SimTruth");
// Setup address
    std::vector<JPSimTrack_t> *track_list = new std::vector<JPSimTrack_t>;
    sim_truth->SetBranchAddress("trackList", &track_list);
// Define variables in looping
    JPSimTrack_t track;
    std::vector<JPSimStepPoint_t> steps;
    JPSimStepPoint_t start, end, temp_step;
    TH1D *hist_y = new TH1D("", "Relative_Vector_Y_Component", 155, 0, 155);
    TH1D *hist_radius = new TH1D("", "Relative_X-Z_Radius_Component", 110, 0, 110);
    TH1D *hist_y_complete = new TH1D("", "Relative_Vector_Complete_Y_Component", 155, 0, 155);
    TH1D *hist_radius_complete = new TH1D("", "Relative_Complete_X-Z_Radius_Component", 200, 0, 200);
    TH1D *hist_steps = new TH1D("", "Steps", 20, 0, 20);
    TH1D *hist_incident_1 = new TH1D("", "Ref_1_Incident_Cos", 20, -1, 1);
    TH1D *hist_incident_2_1 = new TH1D("", "Ref_2_First_Incident_Cos", 20, -1, 1);
    TH1D *hist_incident_2_2 = new TH1D("", "Ref_2_Second_Incident_Cos", 20, -1, 1);
    TH2D *hist_x_y = new TH2D("", "X_Y", 2000, -1000, 1000, 2000, -1000, 1000);
    Double_t radius, y_component;
    Double_t PMT_X, PMT_Y, PMT_Z, PMT_Len;
    Double_t PMT_Cir_X, PMT_Cir_Y, PMT_Cir_Z;
    Double_t CosTheta;
    if (PMT == 0) // Cali PMT
    {
        PMT_Len = 75; // Unit: mm
        PMT_X = 344.15;         PMT_Y = 446.9;            PMT_Z = 0.15;   
        PMT_Cir_X = 490.53;     PMT_Cir_Y = 593.28;        PMT_Cir_Z = 0.15;
    }
    else if(PMT == 1) // Test PMT
    {
        PMT_Len = 75; // Unit: mm
        PMT_X = -430.0;         PMT_Y = -384.82;            PMT_Z = 0.15;
        PMT_Cir_X = -430.0;     PMT_Cir_Y = -591.82;        PMT_Cir_Z = 0.15;
    }
    else if(PMT == 2) // Test PMT + Con
    {
        PMT_Len = 50; // Unit: mm
        PMT_X = -430.0;         PMT_Y = -384.82;            PMT_Z = 0.15;
        PMT_Cir_X = -430.0;     PMT_Cir_Y = -591.82;        PMT_Cir_Z = 0.15;
    }
    TVector3 Pos_end(1, 0, 0), Pos_pmt(PMT_X, PMT_Y, PMT_Z), Pos_relative(1, 0, 0);
    TVector3 Normal(PMT_X - PMT_Cir_X, PMT_Y - PMT_Cir_Y, 0); Normal = Normal.Unit();
    TVector3 Mom_before(1, 0, 0), Mom_after(1, 0, 0), Mom_normal(1, 0, 0);
    Double_t Number_photon = 0, temp_number = 0;
// Loop data
    for(int index = 0; index < sim_truth->GetEntries(); index++)
    {
        sim_truth->GetEntry(index);
        // std::cout << "[Count_Photon] Info about " << index << " entry." << std::endl;
        for (int itrack = 0; itrack < track_list->size(); itrack++)
        {
            track = track_list->at(itrack);
            // std::cout << "[Count_Photon] Info about " << itrack << " track." << std::endl;
            steps = track.StepPoints;
            end = steps.back();
            // Selection criteria: eliminate photons that hit the boundary of box
            if (end.fX == 690 || end.fX == -690) {continue;};
            if (end.fY == 740 || end.fY == -740) {continue;};
            if (end.fZ == 169.85 || end.fZ == -169.85) {continue;};
            // Selection criteria: 
            Pos_end.SetXYZ(end.fX, end.fY, end.fZ);
            Pos_relative = Pos_pmt - Pos_end;
            y_component = Pos_relative.Dot(Normal);
            radius = sqrt(Pos_relative.Mag2() - y_component * y_component);
            // Count Complete Y component and radius distribution for PMT
            if ( y_component < 0) {continue;}; // Skip photons that hit another PMT
            hist_y_complete->Fill(y_component);
            hist_radius_complete->Fill(radius);
            // Selection criteria:
            if (y_component < 0 || y_component > PMT_Len){continue;} // Skip the photon that doesn't hit Test PMT
            if (radius > 105) {continue;}; // PMT最大半径为103mm，如果比105还大就直接排除
            // Count Y component and radius distribution of PMT
            hist_y->Fill(y_component);
            hist_radius->Fill(radius);
            hist_steps->Fill(steps.size());
            hist_x_y->Fill(end.fX, end.fY);
            // Count Photons
            if (steps.size() == 4)
            {
                // Get Info of incident and reflected vectors
                Mom_before = Compute_Direction(0, 1, steps);
                Mom_after = Compute_Direction(2, 3, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                CosTheta = Mom_normal.Dot(Mom_after);
                temp_number = 1 * Compute_Reflectivity(CosTheta, Wavelength);
                Number_photon = Number_photon + temp_number;
                hist_incident_1->Fill(CosTheta);
            }
            else if (steps.size() == 6)
            {
                // First Reflection
                Mom_before = Compute_Direction(0, 1, steps);
                Mom_after = Compute_Direction(2, 3, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                hist_incident_2_1->Fill(Mom_normal.Dot(Mom_after));
                temp_number = 1 * Compute_Reflectivity(CosTheta, Wavelength);
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                hist_incident_2_2->Fill(Mom_normal.Dot(Mom_after));
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                Number_photon = Number_photon + temp_number;
            }
            else if (steps.size() == 8)
            {
                // First Reflection
                Mom_before = Compute_Direction(0, 1, steps);
                Mom_after = Compute_Direction(2, 3, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = 1 * Compute_Reflectivity(CosTheta, Wavelength);
                hist_incident_2_1->Fill(Mom_normal.Dot(Mom_after));
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                hist_incident_2_2->Fill(Mom_normal.Dot(Mom_after));
                // Third Reflection
                Mom_before = Compute_Direction(4, 5, steps);
                Mom_after = Compute_Direction(6, 7, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                // Record
                Number_photon = Number_photon + temp_number;
            }
            else if (steps.size() == 10)
            {
                // First Reflection
                Mom_before = Compute_Direction(0, 1, steps);
                Mom_after = Compute_Direction(2, 3, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = 1 * Compute_Reflectivity(CosTheta, Wavelength);
                hist_incident_2_1->Fill(Mom_normal.Dot(Mom_after));
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                hist_incident_2_2->Fill(Mom_normal.Dot(Mom_after));
                // Third Reflection
                Mom_before = Compute_Direction(4, 5, steps);
                Mom_after = Compute_Direction(6, 7, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                // Forth Reflection
                Mom_before = Compute_Direction(6, 7, steps);
                Mom_after = Compute_Direction(8, 9, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
                // Record
                Number_photon = Number_photon + temp_number;
            }
            else
            {
                Number_photon ++;
            };
        };
    };
//输出
    gROOT->SetBatch(kTRUE); // 不显示Hist
    std::string Title, Pic_Path;
    if(PMT == 0)
    {
        Title = "Cali: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Y.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Y.jpg";
    };
    TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y->SetTitle(Title.c_str());
    hist_y->SetXTitle("Y-Component (mm)");
    hist_y->SetYTitle("Entries");
    hist_y->GetXaxis()->CenterTitle(1);
    hist_y->GetYaxis()->CenterTitle(1);
    hist_y->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    delete canvas;

    if(PMT == 0)
    {
        Title = "Cali: Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Radius.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Radius.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius->SetTitle(Title.c_str());
    hist_radius->SetXTitle("Radius (mm)");
    hist_radius->SetYTitle("Entries");
    hist_radius->GetXaxis()->CenterTitle(1);
    hist_radius->GetYaxis()->CenterTitle(1);
    hist_radius->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    delete canvas;

    if(PMT == 0)
    {
        Title = "Cali: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Y_Complete.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Y_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y_complete->SetTitle(Title.c_str());
    hist_y_complete->SetXTitle("Y-Component (mm)");
    hist_y_complete->SetYTitle("Entries");
    hist_y_complete->GetXaxis()->CenterTitle(1);
    hist_y_complete->GetYaxis()->CenterTitle(1);
    hist_y_complete->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    delete canvas;

    if(PMT == 0)
    {
        Title = "Cali: Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Radius_Complete.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Relative Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Radius_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius_complete->SetTitle(Title.c_str());
    hist_radius_complete->SetXTitle("Radius (mm)");
    hist_radius_complete->SetYTitle("Entries");
    hist_radius_complete->GetXaxis()->CenterTitle(1);
    hist_radius_complete->GetYaxis()->CenterTitle(1);
    hist_radius_complete->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    // Steps
    delete canvas;

    if(PMT == 0)
    {
        Title = "Cali: Steps";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Steps.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Steps";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Steps.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_steps->SetTitle(Title.c_str());
    hist_steps->SetXTitle("Steps");
    hist_steps->SetYTitle("Entries");
    hist_steps->GetXaxis()->CenterTitle(1);
    hist_steps->GetYaxis()->CenterTitle(1);
    canvas->SetLogy();
    hist_steps->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    // One Reflection
    delete canvas;
    
    if(PMT == 0)
    {
        Title = "Cali: Incident Angle Distribution of One Ref";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_One_Ref.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Incident Angle Distribution of One Ref";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_One_Ref.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_incident_1->SetTitle(Title.c_str());
    hist_incident_1->SetXTitle("Cos#theta");
    hist_incident_1->SetYTitle("Entries");
    hist_incident_1->GetXaxis()->CenterTitle(1);
    hist_incident_1->GetYaxis()->CenterTitle(1);
    hist_incident_1->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

    // Two Reflection
    delete canvas;
    
    if(PMT == 0)
    {
        Title = "Cali: Incident Angle Distribution of Two Ref";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Two_Ref.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: Incident Angle Distribution of Two Ref";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Two_Ref.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_incident_2_1->SetTitle(Title.c_str());
    hist_incident_2_1->SetXTitle("Cos#theta");
    hist_incident_2_1->SetYTitle("Entries");
    hist_incident_2_1->GetXaxis()->CenterTitle(1);
    hist_incident_2_1->GetYaxis()->CenterTitle(1);
    hist_incident_2_1->SetLineColor(kBlack);
    hist_incident_2_1->Draw();
    hist_incident_2_2->SetLineColor(kRed);
    hist_incident_2_2->SetLineStyle(10);
    hist_incident_2_2->Draw("SAME");
    // 图例
    TLegend *legend = new TLegend(0.3, 0.7, 0.5, 0.9);
    legend->AddEntry(hist_incident_2_1, "Fist", "l");
    legend->AddEntry(hist_incident_2_2, "Second", "l");
    legend->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    // X_Y
    if(PMT == 0)
    {
        Title = "Cali: X_Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_X_Y.jpg";
    }
    else if(PMT == 1 || PMT == 2)
    {
        Title = "Test: X_Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_X_Y.jpg";
    };
    
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_x_y->SetTitle(Title.c_str());
    hist_x_y->SetXTitle("X/mm");
    hist_x_y->SetYTitle("Y/mm");
    hist_x_y->GetXaxis()->CenterTitle(1);
    hist_x_y->GetYaxis()->CenterTitle(1);
    hist_x_y->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();

// 释放内存
    delete canvas;
    delete hist_y;
    delete hist_radius;
    delete track_list;
    delete file;
// 返回
    return Number_photon;
}

void Count_Photon(Int_t &Num_Cali, Int_t &Num_Test, Double_t &Ratio, std::string File_Path, std::string Pic_Dir, std::string strings, Int_t wavelength)
{
    Num_Cali = Count_PMT_Photon(0, File_Path.c_str(), Pic_Dir, strings, wavelength);
    Num_Test = Count_PMT_Photon(1, File_Path.c_str(), Pic_Dir, strings, wavelength);
    Ratio = 1.0 * Num_Test / Num_Cali;
};

void Count_Photon_Con(Int_t &Num_Cali, Int_t &Num_Test, Double_t &Ratio, std::string File_Path, std::string Pic_Dir, std::string strings, Int_t wavelength)
{
    Num_Cali = Count_PMT_Photon(0, File_Path.c_str(), Pic_Dir, strings, wavelength);
    Num_Test = Count_PMT_Photon(2, File_Path.c_str(), Pic_Dir, strings, wavelength);
    Ratio = 1.0 * Num_Test / Num_Cali;
};

void Count_Photon_All(std::string File_Dir, std::string Pic_Dir, std::string CSV_File, std::string concentrator, Int_t Wavelength, Int_t Distance)
{
    // Paths of Files, Pics and CSV Files
    // std::string File, File_Dir, File_Path, Pic_Dir, CSV_File;

    // Variables in Loop
    Int_t Num_Cali, Num_Test;
    std::string file, res;
    // std::string concentrator = "1";
    std::vector<std::string> head_info;
    Double_t Ratio;

    // File_Dir = "/home/penguin/Jinping/JSAP-install/Simulation/Concentrator-Simulation/OutputFiles/Photon_Concentrator/L1/Average";
    // Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/L1";
    // CSV_File = "/home/penguin/Jinping/JSAP-install/Codes/CSV/L1_Con.csv";

    std::cout << "[Count_Photon::Count_Photon_All] Data Dir: " << File_Dir << std::endl;
    std::cout << "[Count_Photon::Count_Photon_All] Pic Dir: " << Pic_Dir << std::endl;
    std::cout << "[Count_Photon::Count_Photon_All] CSV File: " << CSV_File << std::endl;
    std::cout << "[Count_Photon::Count_Photon_All] Wavelength: " << Wavelength << std::endl;

    // Writing in CSV File
    std::ofstream csv_file(CSV_File, std::ios::trunc);
    std::string head = "angle,angle_error,distance,concentrator,led,ball/temperature,test_photon,test_photon_error,cali_photon,cali_photon_error,ratio,ratio_error";
    csv_file << head << std::endl;

    std::vector<std::string> Abs_Files = Get_All_Files(File_Dir);
    std::vector<std::string> File_Names = Extract_File_Names(Abs_Files);
    std::vector<std::string> Names = Extract_Names(File_Names);
    Double_t Num_Test_Error, Num_Cali_Error, Ratio_Error;
    for(int index = 0; index < Names.size(); index++)
    {
        std::cout << "[Count_Photon::Count_Photon_All] Processing File: " << File_Names.at(index) << std::endl;
        file = File_Names.at(index);
        
        head_info = Collect_Info(file);
        res = head_info.at(0) + "," + head_info.at(1) + "," + head_info.at(2) + "," + concentrator + "," + head_info.at(3) + "," + head_info.at(4);
        if (concentrator == "0")
        {
            Count_Photon(Num_Cali, Num_Test, Ratio, Abs_Files.at(index), Pic_Dir, Names.at(index), Wavelength);
        }
        else if(concentrator == "1")
        {
            Count_Photon_Con(Num_Cali, Num_Test, Ratio, Abs_Files.at(index), Pic_Dir, Names.at(index), Wavelength);
        };
        // Compute Error
        Num_Test_Error = sqrt(Num_Test);
        Num_Cali_Error = sqrt(Num_Cali);
        Ratio_Error = (1.0 * Num_Test / Num_Cali) * sqrt( pow(Num_Test_Error / Num_Test, 2) + pow(Num_Cali_Error / Num_Cali, 2));
        
        // Record Photons
        res = res + "," + std::to_string(Num_Test) + "," + std::to_string(Num_Test_Error) + ",";
        res = res + std::to_string(Num_Cali) + "," + std::to_string(Num_Cali_Error) + ",";
        res = res + std::to_string(Ratio) + "," + std::to_string(Ratio_Error);
        
        // Writting in CSV File
        if(head_info.at(0) == "90" && Distance == 1)
        {
            csv_file << res;
        }
        else if(head_info.at(0) == "85" && Distance == 2)
        {
            csv_file << res;
        }
        else
        {
            csv_file << res << std::endl;
        }
    };

    // Close CSV File
    csv_file.close();
};


// 以下代码针对新的几何。PMT玻璃有折射率，Cathode会吸收光子
int Count_PMT_Photon_Cathode(Int_t PMT, std::string File_Path, std::string Pic_Dir, std::string strings)
{
    // std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test.root";
// Open the file
    TFile *file = new TFile(File_Path.c_str());
    TTree *sim_truth = (TTree*) file->Get("SimTruth");
// Setup address
    std::vector<JPSimTrack_t> *track_list = new std::vector<JPSimTrack_t>;
    sim_truth->SetBranchAddress("trackList", &track_list);
// Define variables in looping
    JPSimTrack_t track;
    std::vector<JPSimStepPoint_t> steps;
    JPSimStepPoint_t start, end, temp_step;
    TH1D *hist_y = new TH1D("", "Relative_Vector_Y_Component", 155, 0, 155);
    TH1D *hist_radius = new TH1D("", "Relative_X-Z_Radius_Component", 110, 0, 110);
    TH1D *hist_y_complete = new TH1D("", "Relative_Vector_Complete_Y_Component", 155, 0, 155);
    TH1D *hist_radius_complete = new TH1D("", "Relative_Complete_X-Z_Radius_Component", 200, 0, 200);
    TH1D *hist_steps = new TH1D("", "Steps", 50, 0, 50);
    Double_t radius, y_component;
    Double_t PMT_X, PMT_Y, PMT_Z, PMT_Len;
    Double_t PMT_Cir_X, PMT_Cir_Y, PMT_Cir_Z;
    if (PMT == 0) // Cali PMT
    {
        PMT_Len = 75; // Unit: mm
        PMT_X = 344.15 + 1.414;         PMT_Y = 446.9 + 1.414;            PMT_Z = 0.15;   
        PMT_Cir_X = 490.53;     PMT_Cir_Y = 593.28;        PMT_Cir_Z = 0.15;
    }
    else if(PMT == 1) // Test PMT
    {
        PMT_Len = 75; // Unit: mm
        PMT_X = -430.0;         PMT_Y = -384.82 - 2;            PMT_Z = 0.15;
        PMT_Cir_X = -430.0;     PMT_Cir_Y = -591.82;        PMT_Cir_Z = 0.15;
    }
    else if(PMT == 2) // Test PMT + Con
    {
        PMT_Len = 50; // Unit: mm
        PMT_X = -430.0;         PMT_Y = -384.82 - 2;            PMT_Z = 0.15;
        PMT_Cir_X = -430.0;     PMT_Cir_Y = -591.82;        PMT_Cir_Z = 0.15;
    }
    TVector3 Pos_end(1, 0, 0), Pos_pmt(PMT_X, PMT_Y, PMT_Z), Pos_relative(1, 0, 0);
    TVector3 Normal(PMT_X - PMT_Cir_X, PMT_Y - PMT_Cir_Y, 0); Normal = Normal.Unit();
    Int_t Number_photon = 0;
// Loop data
    for(int index = 0; index < sim_truth->GetEntries(); index++)
    {
        sim_truth->GetEntry(index);
        // std::cout << "[Count_Photon] Info about " << index << " entry." << std::endl;
        for (int itrack = 0; itrack < track_list->size(); itrack++)
        {
            track = track_list->at(itrack);
            // std::cout << "[Count_Photon] Info about " << itrack << " track." << std::endl;
            steps = track.StepPoints;
            end = steps.back();
            // Selection criteria: eliminate photons that hit the boundary of box
            if (end.fX == 690 || end.fX == -690) {continue;};
            if (end.fY == 740 || end.fY == -740) {continue;};
            if (end.fZ == 169.85 || end.fZ == -169.85) {continue;};
            
            // Selection criteria: 
            Pos_end.SetXYZ(end.fX, end.fY, end.fZ);
            Pos_relative = Pos_pmt - Pos_end;
            y_component = Pos_relative.Dot(Normal);
            radius = sqrt(Pos_relative.Mag2() - y_component * y_component);
            // Count Complete Y component and radius distribution for PMT
            if ( y_component < 0) {continue;}; // Skip photons that hit another PMT
            hist_y_complete->Fill(y_component);
            hist_radius_complete->Fill(radius);
            // Selection criteria:
            if (y_component < 0 || y_component > PMT_Len){continue;} // Skip the photon that doesn't hit Test PMT
            if (radius > 105) {continue;};
            // Count Y component and radius distribution of PMT
            hist_y->Fill(y_component);
            hist_radius->Fill(radius);
            hist_steps->Fill(steps.size());
            Number_photon ++;
        };
    };
//输出
    gROOT->SetBatch(kTRUE); // 不显示Hist
    std::string Title, Pic_Path;
    // Relative Y Component after selection cut
    if(PMT == 0)
    {
        Title = "Cali: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Y.jpg";
    }
    else if(PMT == 1)
    {
        Title = "Test: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Y.jpg";
    };
    TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y->SetTitle(Title.c_str());
    hist_y->SetXTitle("Y-Component (mm)");
    hist_y->SetYTitle("Entries");
    hist_y->GetXaxis()->CenterTitle(1);
    hist_y->GetYaxis()->CenterTitle(1);
    hist_y->Draw();
    canvas->SaveAs(Pic_Path.c_str());
    canvas->Close();

    delete canvas;
    // Relative Radius after selection cut
    if(PMT == 0)
    {
        Title = "Cali: Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Radius.jpg";
    }
    else if(PMT == 1)
    {
        Title = "Test: Relative Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Radius.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius->SetTitle(Title.c_str());
    hist_radius->SetXTitle("Radius (mm)");
    hist_radius->SetYTitle("Entries");
    hist_radius->GetXaxis()->CenterTitle(1);
    hist_radius->GetYaxis()->CenterTitle(1);
    hist_radius->Draw();
    canvas->SaveAs(Pic_Path.c_str());
    canvas->Close();

    delete canvas;
    // Relative Y Component 
    if(PMT == 0)
    {
        Title = "Cali: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Y_Complete.jpg";
    }
    else if(PMT == 1)
    {
        Title = "Test: Relative Vecotor Y Component";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Y_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y_complete->SetTitle(Title.c_str());
    hist_y_complete->SetXTitle("Y-Component (mm)");
    hist_y_complete->SetYTitle("Entries");
    hist_y_complete->GetXaxis()->CenterTitle(1);
    hist_y_complete->GetYaxis()->CenterTitle(1);
    hist_y_complete->Draw();
    canvas->SaveAs(Pic_Path.c_str());
    canvas->Close();

    delete canvas;
    // Relative Radius
    if(PMT == 0)
    {
        Title = "Cali: Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Radius_Complete.jpg";
    }
    else if(PMT == 1)
    {
        Title = "Test: Relative Relative Radius";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Radius_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius_complete->SetTitle(Title.c_str());
    hist_radius_complete->SetXTitle("Radius (mm)");
    hist_radius_complete->SetYTitle("Entries");
    hist_radius_complete->GetXaxis()->CenterTitle(1);
    hist_radius_complete->GetYaxis()->CenterTitle(1);
    hist_radius_complete->Draw();
    canvas->SaveAs(Pic_Path.c_str());
    canvas->Close();

    delete canvas;
    // Steps
    if(PMT == 0)
    {
        Title = "Cali: Steps";
        Pic_Path = Pic_Dir + "/" + strings + "_Cali_Steps.jpg";
    }
    else if(PMT == 1)
    {
        Title = "Test: Steps";
        Pic_Path = Pic_Dir + "/" + strings + "_Test_Steps.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_steps->SetTitle(Title.c_str());
    hist_steps->SetXTitle("Steps");
    hist_steps->SetYTitle("Entries");
    hist_steps->GetXaxis()->CenterTitle(1);
    hist_steps->GetYaxis()->CenterTitle(1);
    canvas->SetLogy();
    hist_steps->Draw();
    canvas->SaveAs(Pic_Path.c_str());
    canvas->Close();
// 释放内存
    delete canvas;
    delete hist_y;
    delete hist_radius;
    delete track_list;
    delete file;
// 返回
    return Number_photon;
}

void Count_Photon_Cathode(Int_t &Num_Cali, Int_t &Num_Test, Double_t &Ratio, std::string File_Path, std::string Pic_Dir, std::string strings)
{
    Num_Cali = Count_PMT_Photon_Cathode(0, File_Path.c_str(), Pic_Dir, strings);
    Num_Test = Count_PMT_Photon_Cathode(1, File_Path.c_str(), Pic_Dir, strings);
    Ratio = 1.0 * Num_Test / Num_Cali;
};

void Count_Photon_All_Cathode(std::string File_Dir, std::string Pic_Dir, std::string CSV_File, std::string concentrator)
{
    // Paths of Files, Pics and CSV Files
    // std::string File, File_Dir, File_Path, Pic_Dir, CSV_File;

    // Variables in Loop
    Int_t Num_Cali, Num_Test;
    std::string file, res;
    // std::string concentrator = "1";
    std::vector<std::string> head_info;
    Double_t Ratio;

    // File_Dir = "/home/penguin/Jinping/JSAP-install/Simulation/Concentrator-Simulation/OutputFiles/Photon_Concentrator/L1/Average";
    // Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/L1";
    // CSV_File = "/home/penguin/Jinping/JSAP-install/Codes/CSV/L1_Con.csv";

    std::cout << "[Count_Photon::Count_Photon_All] Data Dir: " << File_Dir << std::endl;
    std::cout << "[Count_Photon::Count_Photon_All] Pic Dir: " << Pic_Dir << std::endl;
    std::cout << "[Count_Photon::Count_Photon_All] CSV File: " << CSV_File << std::endl;

    // Writing in CSV File
    std::ofstream csv_file(CSV_File, std::ios::trunc);
    std::string head = "angle,angle_error,distance,concentrator,led,ball/temperature,test_photon,cali_photon,ratio";
    csv_file << head << std::endl;

    std::vector<std::string> Abs_Files = Get_All_Files(File_Dir);
    std::vector<std::string> File_Names = Extract_File_Names(Abs_Files);
    std::vector<std::string> Names = Extract_Names(File_Names);
    for(int index = 0; index < Names.size(); index++)
    {
        std::cout << "[Count_Photon::Count_Photon_All] Processing File: " << File_Names.at(index) << std::endl;
        file = File_Names.at(index);
        
        head_info = Collect_Info(file);
        res = head_info.at(0) + "," + head_info.at(1) + "," + head_info.at(2) + "," + concentrator + "," + head_info.at(3) + "," + head_info.at(4);
        if (concentrator == "0")
        {
            Count_Photon_Cathode(Num_Cali, Num_Test, Ratio, Abs_Files.at(index), Pic_Dir, Names.at(index));
        }
        else if(concentrator == "1")
        {
            // Count_Photon_Con(Num_Cali, Num_Test, Ratio, Abs_Files.at(index), Pic_Dir, Names.at(index));
            std::cout << "[Count_Photon::Count_Photon_All_Cathode] Empty!!!" << std::endl;
        };
        
        // Record Photons
        res = res + "," + std::to_string(Num_Test) + "," + std::to_string(Num_Cali) + "," + std::to_string(Ratio);
        
        // Writting in CSV File
        if(head_info.at(0) == "90")
        {
            csv_file << res;
        }
        else
        {
            csv_file << res << std::endl;
        }
    };

    // Close CSV File
    csv_file.close();

};


#endif