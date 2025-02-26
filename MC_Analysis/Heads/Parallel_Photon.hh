#ifndef PARALLEL_PHOTON_HH
#define PARALLEL_PHOTON_HH
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
#include <TStyle.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined
#include "./Count_Photon.hh"

std::vector<TVector3> Check_Light_Source(Int_t PMT, std::string File_Path, std::string Pic_Dir, std::string Strings)
{
    // std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test_1000k_0.root";
// Open the file
    TFile *file = new TFile(File_Path.c_str());
    TTree *sim_truth = (TTree*) file->Get("SimTruth");
// Setup address
    Double_t pos_x, pos_y, pos_z;
    sim_truth->SetBranchAddress("x", &pos_x);
    sim_truth->SetBranchAddress("y", &pos_y);
    sim_truth->SetBranchAddress("z", &pos_z);
    Double_t mom_x, mom_y, mom_z;
    sim_truth->SetBranchAddress("PrimaryParticleList.px", &mom_x);
    sim_truth->SetBranchAddress("PrimaryParticleList.py", &mom_y);
    sim_truth->SetBranchAddress("PrimaryParticleList.pz", &mom_z);
// Define variables in looping
    TVector3 pos;
    TH1D *hist_radius = new TH1D("", "Radius", 60, 0, 600);
    TH1D *hist_z = new TH1D("", "Z", 500, 0, 500);
    TH2D *hist_x_z = new TH2D("", "X_Z", 2000, -1000, 1000, 2000, -1000, 1000);
    TH2D *hist_x_y = new TH2D("", "X_Y", 2000, -1000, 1000, 2000, -1000, 1000);
    TH2D *hist_y_z = new TH2D("", "Y_Z", 2000, -1000, 1000, 2000, -1000, 1000);
// Compute Theta
    TVector3 Pos[3];
    TVector3 Mom;
    for(int index = 0; index < 4; index++)
    {
        sim_truth->GetEntry(index);
        Pos[index].SetXYZ(pos_x, pos_y, pos_z);
        Mom.SetXYZ(mom_x, mom_y, mom_z);
    };
    TVector3 Re_Pos[2];
    Re_Pos[0] = Pos[0] - Pos[1];
    Re_Pos[1] = Pos[0] - Pos[2];
    Re_Pos[0] = Re_Pos[0].Unit();
    Re_Pos[1] = Re_Pos[1].Unit();
    TVector3 Cross;
    Cross = Re_Pos[1].Cross(Re_Pos[0]);
    Cross = Cross.Unit();
    std::cout << "[Check_Light_Source] Plane X: " << Cross.X() << ", Y: " << Cross.Y() << ", Z: " << Cross.Z() << std::endl;
    Mom = Mom.Unit();
    std::cout << "[Check_Light_Source] Particle Direction X: " << Mom.X() << ", Y: " << Mom.Y() << ", Z: " << Mom.Z() << std::endl;
    std::vector<TVector3> res;
    res.push_back(Cross);
    res.push_back(Mom);
// Loop data
    for(int index = 0; index < sim_truth->GetEntries(); index++)
    {
        sim_truth->GetEntry(index);
        pos.SetXYZ(pos_x, pos_y, pos_z);
        hist_z->Fill(pos_z);
        hist_radius->Fill(pos.Perp());
        hist_x_z->Fill(pos.X(), pos.Z());
        hist_x_y->Fill(pos.X(), pos.Y());
        hist_y_z->Fill(pos.Y(), pos.Z());
    };
// Output
//  // X-Z
    gROOT->SetBatch(kTRUE);
    gStyle->SetOptStat(0);
    std::string Title, Pic_Path;
    if(PMT == 1)
    {
        Title = "PMT: Light_Source_X_Z";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Light_Source_X_Z.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Light_Source_X_Z";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Light_Source_X_Z.jpg";
    }
    TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_x_z->SetTitle(Title.c_str());
    hist_x_z->SetXTitle("X(mm)");
    hist_x_z->SetYTitle("Z(mm)");
    hist_x_z->GetXaxis()->CenterTitle(1);
    hist_x_z->GetYaxis()->CenterTitle(1);
    hist_x_z->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
//  // X-Y
    if(PMT == 1)
    {
        Title = "PMT: Light_Source_X_Y";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Light_Source_X_Y.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Light_Source_X_Y";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Light_Source_X_Y.jpg";
    }
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_x_y->SetTitle(Title.c_str());
    hist_x_y->SetXTitle("X(mm)");
    hist_x_y->SetYTitle("Y(mm)");
    hist_x_y->GetXaxis()->CenterTitle(1);
    hist_x_y->GetYaxis()->CenterTitle(1);
    hist_x_y->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
//  // Y-Z
    if(PMT == 1)
    {
        Title = "PMT: Light_Source_Y_Z";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Light_Source_Y_Z.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Light_Source_Y_Z";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Light_Source_Y_Z.jpg";
    }
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y_z->SetTitle(Title.c_str());
    hist_y_z->SetXTitle("Y(mm)");
    hist_y_z->SetYTitle("Z(mm)");
    hist_y_z->GetXaxis()->CenterTitle(1);
    hist_y_z->GetYaxis()->CenterTitle(1);
    hist_y_z->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
// Output
    return res;
};

Double_t Count_Parallel_Photon(Int_t PMT, std::string File_Path, std::string Pic_Dir, std::string Strings, Int_t Wavelength, std::vector<TVector3> &Directions)
{
    // std::string Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/test";
    // Int_t PMT = 1;
    // Int_t Wavelength = 415;
    // std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test_1000k_0_PMT.root";
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
    TVector3 pos;
    TH1D *hist_y = new TH1D("", "Relative_Vector_Y_Component", 155, 0, 155);
    TH1D *hist_y_complete = new TH1D("", "Relative_Vector_Complete_Y_Component", 155, 0, 155);
    TH1D *hist_radius = new TH1D("", "Relative_Radius_Component", 110, 0, 110);
    TH1D *hist_radius_complete = new TH1D("", "Complete_Relative_Radius_Component", 110, 0, 110);
    TH1D *hist_steps = new TH1D("", "Steps", 20, 0, 20);
    TH2D *hist_x_z = new TH2D("", "X_Z", 400, -400, 400, 600, -300, 300);
    TH2D *hist_x_y = new TH2D("","X_Y", 800, -400, 400, 800, -400, 400);
    Double_t PMT_X, PMT_Y, PMT_Z, PMT_Len;
    Double_t PMT_Cir_X, PMT_Cir_Y, PMT_Cir_Z;
    Double_t y_component, radius;
    if (PMT == 1)
    {
        PMT_Len = 50;
        PMT_X = 0;          PMT_Y = 0;          PMT_Z = 152;
        PMT_Cir_X = 0;      PMT_Cir_Y = 0;      PMT_Cir_Z = 0;
    }
    else if(PMT == 2)
    {
        PMT_Len = 50; // Unit: mm
        PMT_X = 0;          PMT_Y = 0;          PMT_Z = 152;
        PMT_Cir_X = 0;      PMT_Cir_Y = 0;      PMT_Cir_Z = 0;
    };
    TVector3 Pos_pmt(PMT_X, PMT_Y, PMT_Z), Pos_end(1, 0, 0), Pos_relative(1, 0, 0);
    TVector3 Normal(PMT_X - PMT_Cir_X, PMT_Y - PMT_Cir_Y, PMT_Z - PMT_Cir_Z);   Normal = Normal.Unit();
    TVector3 Mom_before, Mom_after, Mom_normal;
    Double_t CosTheta, temp_number, Number_photon;
// Loop data
    for(int index = 0; index < sim_truth->GetEntries(); index++)
    {
        sim_truth->GetEntry(index);
        for (int itrack = 0; itrack < track_list->size(); itrack++)
        {
            track = track_list->at(itrack);
            steps = track.StepPoints;
            end = steps.back();
            pos.SetXYZ(end.fX, end.fY, end.fZ);
        // Selection criteria: eliminate photons that hit the boundary of box
            if (end.fX == 2500 || end.fX == -2500) {continue;};
            if (end.fY == 2500 || end.fY == -2500) {continue;};
            if (end.fZ == 2500 || end.fZ == -2500) {continue;};
        // Selection criteria:
            Pos_end.SetXYZ(end.fX, end.fY, end.fZ);
            Pos_relative = Pos_pmt - Pos_end;
            y_component = Pos_relative.Dot(Normal);
            radius = sqrt(Pos_relative.Mag2() - y_component * y_component);
            hist_y_complete->Fill(y_component);
            hist_radius_complete->Fill(radius);
            if(y_component < 0 || y_component > PMT_Len) {continue;};
            if(radius > 105){continue;};
        // Record data
            hist_y->Fill(y_component);
            hist_radius->Fill(radius);
            hist_x_z->Fill(pos.X(), pos.Z());
            hist_x_y->Fill(pos.X(), pos.Y());
            hist_steps->Fill(steps.size());
        // Cout Photons
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
            }
            else if (steps.size() == 6)
            {
                // First Reflection
                Mom_before = Compute_Direction(0, 1, steps);
                Mom_after = Compute_Direction(2, 3, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = 1 * Compute_Reflectivity(CosTheta, Wavelength);
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
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
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
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
                // Second Reflection
                Mom_before = Compute_Direction(2, 3, steps);
                Mom_after = Compute_Direction(4, 5, steps);
                Mom_normal = Mom_after - Mom_before;
                Mom_normal = Mom_normal.Unit();
                temp_number = temp_number * Compute_Reflectivity(CosTheta, Wavelength);
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
// Output
    Directions = Check_Light_Source(PMT, File_Path, Pic_Dir, Strings);
    gROOT->SetBatch(kTRUE);
    gStyle->SetOptStat(1);
    std::string Title, Pic_Path;
    std::cout << "[Parallel_Photon::Count_Parallel_Photon] The Pics are in " << Pic_Dir << std::endl;
//  // Relative Y Component
    if(PMT == 1)
    {
        Title = "PMT: Relative Vector Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Y.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Relative Vector Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Y.jpg";
    };
    TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y->SetTitle(Title.c_str());
    hist_y->SetXTitle("Y-Component(mm)");
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
//  // Complete Y Component
    if(PMT == 1)
    {
        Title = "PMT: Complete Relative Vector Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Y_Complete.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Complete Relative Vector Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Y_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_y_complete->SetTitle(Title.c_str());
    hist_y_complete->SetXTitle("Y-Component(mm)");
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
//  // Relative Radius
    if(PMT == 1)
    {
        Title = "PMT: Relative Radius";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_R.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Relative Radius";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_R.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius->SetTitle(Title.c_str());
    hist_radius->SetXTitle("Radius(mm)");
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
//  // Relative Radius
    if(PMT == 1)
    {
        Title = "PMT: Complete Relative Radius";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_R_Complete.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Complete Relative Radius";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_R_Complete.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_radius_complete->SetTitle(Title.c_str());
    hist_radius_complete->SetXTitle("Radius(mm)");
    hist_radius_complete->SetYTitle("Entries");
    hist_radius_complete->GetXaxis()->CenterTitle(1);
    hist_radius_complete->GetYaxis()->CenterTitle(1);
    hist_radius_complete->Draw();
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
//  // Steps
    if(PMT == 1)
    {
        Title = "PMT: Steps";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_Steps.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: Steps";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_Steps.jpg";
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
    delete canvas;
//  // X-Z
    gStyle->SetOptStat(0);  // 关闭统计信息
    if(PMT == 1)
    {
        Title = "PMT: X-Z Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_X_Z.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: X-Z Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_X_Z.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_x_z->SetTitle(Title.c_str());
    hist_x_z->SetXTitle("X(mm)");
    hist_x_z->SetYTitle("Z(mm)");
    hist_x_z->GetXaxis()->CenterTitle(1);
    hist_x_z->GetYaxis()->CenterTitle(1);
    hist_x_z->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
//  // X-Y
    gStyle->SetOptStat(0);  // 关闭统计信息
    if(PMT == 1)
    {
        Title = "PMT: X-Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_PMT_X_Y.jpg";
    }
    else if(PMT == 2)
    {
        Title = "Con: X-Y Component";
        Pic_Path = Pic_Dir + "/" + Strings +  "_Con_X_Y.jpg";
    };
    canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist_x_y->SetTitle(Title.c_str());
    hist_x_y->SetXTitle("X(mm)");
    hist_x_y->SetYTitle("Y(mm)");
    hist_x_y->GetXaxis()->CenterTitle(1);
    hist_x_y->GetYaxis()->CenterTitle(1);
    hist_x_y->Draw("COLZ");
    if(Pic_Dir != "0")
    {
        canvas->SaveAs(Pic_Path.c_str());
    }
    canvas->Close();
    delete canvas;
// 释放内存
    delete hist_y;
    delete track_list;
    delete file;
// 返回
    return Number_photon;
};

void Count_Parallel_Photon(Int_t Wavelength, Int_t Concentrator)
{
    std::string Data_Dir = "/mnt/e/PMT/Parallel_Light/01";
    std::string Pic_Dir = "/mnt/e/PMT/Parallel_Light/01/Pics";
    std::string CSV_Dir = "/mnt/e/PMT/Parallel_Light/01/CSV";
    
    Int_t PMT;
    std::string Data_Path, Pic_Path, CSV_File;
    if (Concentrator == 0)
    {
        PMT = 1;
        Data_Path = Data_Dir + "/PMT";
        Pic_Path = Pic_Dir + "/PMT";
        CSV_File = CSV_Dir + "/" + std::to_string(Wavelength) + "_PMT.csv";
    }
    else if(Concentrator == 1)
    {
        PMT = 2;
        Data_Path = Data_Dir + "/Concentrator";
        Pic_Path = Pic_Dir + "/Concentrator";
        CSV_File = CSV_Dir + "/" + std::to_string(Wavelength) + "_Con.csv";
    }
    std::cout << "[Parallel_Phont::Count_Parallel_Photon] Data Dir: " << Data_Path << std::endl;
    std::cout << "[Parallel_Phont::Count_Parallel_Photon] Pic Dir: " << Pic_Path << std::endl;
    std::cout << "[Parallel_Phont::Count_Parallel_Photon] CSV File: " << CSV_File << std::endl;
    // Writing in CSV File
    std::ofstream csv_file(CSV_File, std::ios::trunc);
    std::string head = "angle,concentrator,led,num_photon,num_error_photon,dir_pho_x,dir_pho_y,dir_pho_z,dir_plane_x,dir_plane_y,dir_plane_z";
    csv_file << head << std::endl;

    std::vector<std::string> Abs_Files = Get_All_Files(Data_Path);
    std::vector<std::string> File_Names = Extract_File_Names(Abs_Files);
    std::vector<std::string> Names = Extract_Names(File_Names);
    std::vector<std::string> head_info;
    std::string file, res, string;
    Double_t Num;
    std::vector<TVector3> Source_Info;
    for(int index = 0; index < Names.size(); index++)
    {
        file = Names.at(index);
        head_info = Collect_Info_Parallel_Light(file); // LED, Angle
        string = std::to_string(Wavelength) + "_" + head_info.at(0);
        Num = Count_Parallel_Photon(PMT, Abs_Files.at(index), Pic_Path, string, Wavelength, Source_Info);
        //Compute Error
        Double_t Num_Error = sqrt(Num);
        // Record Photons
        res = head_info.at(0) + "," + std::to_string(Concentrator) + "," + std::to_string(Wavelength) + ",";
        res = res + std::to_string(Num) + "," + std::to_string(Num_Error) + ",";
        res = res + std::to_string(Source_Info.at(0).X()) + "," + std::to_string(Source_Info.at(0).Y()) + ","  + std::to_string(Source_Info.at(0).Z()) + ",";
        res = res + std::to_string(Source_Info.at(1).X()) + "," + std::to_string(Source_Info.at(1).Y()) + "," + std::to_string(Source_Info.at(1).Z());
        // Writting in CSV Fiel
        if(head_info.at(0) == "90")
        {
            csv_file << res;
        }
        else if(head_info.at(0) != "90")
        {
            csv_file << res << std::endl;
        }
    };
    // Close CSV File
    csv_file.close();
}

#endif